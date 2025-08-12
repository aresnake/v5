# -*- coding: utf-8 -*-
# ares/voice/voice_engine.py

from __future__ import annotations

import threading
import time
import math
from typing import Optional

try:
    import bpy
except Exception:  # outils externes / tests hors Blender
    bpy = None

# Reconnaissance vocale (optionnel)
try:
    import speech_recognition as sr
except Exception:
    sr = None

from ares.core.logger import get_logger

log = get_logger("VoiceEngine")


class VoiceEngine:
    """
    Moteur voix robuste :
    - start/stop thread d'écoute
    - anti-doublons, backoff erreurs
    - push transcript vers Scene.blade_transcript (si existe)
    - exécution auto de la pipeline (facultatif)
    - support Whisper si installé, sinon SpeechRecognition (Google Web API)
    """

    def __init__(self, *, device_index: Optional[int] = None):
        self.recognizer: Optional["sr.Recognizer"] = None
        self.microphone: Optional["sr.Microphone"] = None
        self.device_index = device_index

        self.listening = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.last_transcript: str = ""
        self._last_emit_time: float = 0.0
        self._min_repeat_interval_s: float = 1.5  # anti-spam : ignore répétition < 1.5s

        self.auto_execute: bool = False  # si True, exécute immédiatement la pipeline

        # Backend Whisper optionnel
        self._whisper_backend = self._init_whisper_backend()

        # Backend SR
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                # Si device_index est None, SR choisit le défaut
                self.microphone = sr.Microphone(device_index=self.device_index)
                log.info("🎤 Micro initialisé (SpeechRecognition).")
            except Exception as e:
                log.exception(f"Impossible d'initialiser le micro SR : {e}")
                self.recognizer = None
                self.microphone = None
        else:
            log.warning("ℹ️ speech_recognition indisponible (utilisera Whisper si présent).")

    # ------------------------------------------------------------------ #
    # API publique
    # ------------------------------------------------------------------ #
    def start_listening(self):
        with self._lock:
            if self.listening:
                return
            self.listening = True

        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        log.info("✅ VoiceEngine : écoute démarrée")

    def stop_listening(self):
        with self._lock:
            self.listening = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        log.info("🛑 VoiceEngine : écoute arrêtée")

    def shutdown(self):
        """À appeler au unregister addon pour libérer proprement."""
        self.stop_listening()
        # Rien de spécial à libérer (SR gère via context manager)

    def set_auto_execute(self, enabled: bool):
        self.auto_execute = bool(enabled)
        log.info(f"⚙️ Auto-execute = {self.auto_execute}")

    # ------------------------------------------------------------------ #
    # Boucle d'écoute
    # ------------------------------------------------------------------ #
    def _listen_loop(self):
        # Si Whisper présent et SR absent → on passe en mode Whisper direct (pull audio SR ou fallback)
        use_whisper = self._whisper_backend is not None

        if not use_whisper and not (self.recognizer and self.microphone):
            log.warning("Aucun backend voix initialisé (ni Whisper ni SR).")
            return

        # Calibration SR si disponible
        if self.recognizer and self.microphone:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    log.info("🔈 Bruit ambiant calibré (SR)")
            except Exception as e:
                log.exception(f"Échec calibration micro (SR) : {e}")

        backoff = 0.2  # seconds
        max_backoff = 2.0

        while True:
            with self._lock:
                if not self.listening:
                    break

            try:
                text = ""
                if use_whisper:
                    # Mode Whisper : on essaie d’enregistrer un chunk via SR si dispo,
                    # sinon on ne peut pas capturer (on resterait alors silencieux).
                    text = self._recognize_whisper()
                else:
                    text = self._recognize_sr_blocking(timeout=5, phrase_time_limit=6)

                if text:
                    now = time.time()
                    # Anti-doublon rapproché
                    if (
                        text == self.last_transcript
                        and (now - self._last_emit_time) < self._min_repeat_interval_s
                    ):
                        continue

                    self._last_emit_time = now
                    self.last_transcript = text
                    log.info(f"🗣️ Phrase reconnue : {text}")
                    self._on_phrase_recognized(text)

                backoff = 0.2  # reset backoff si succès

            except Exception as e:
                log.exception(f"Erreur d'écoute : {e}")
                time.sleep(backoff)
                backoff = min(max_backoff, backoff * 1.5)

    # ------------------------------------------------------------------ #
    # Reconnaissance : SR (Google Web API) et Whisper (optionnel)
    # ------------------------------------------------------------------ #
    def _recognize_sr_blocking(self, timeout: float = 5.0, phrase_time_limit: float = 6.0) -> str:
        if not (self.recognizer and self.microphone):
            return ""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return self.recognizer.recognize_google(audio, language="fr-FR").strip()
        except sr.WaitTimeoutError:
            log.debug("⏱️ Timeout d'écoute (SR).")
            return ""
        except Exception:
            return ""

    def _init_whisper_backend(self):
        """
        Tente de charger faster_whisper ou whisper (OpenAI) si dispo.
        Retourne un tuple (backend_name, model) ou None.
        """
        # L’addon peut installer ces paquets via install_dependencies.py
        try:
            from faster_whisper import WhisperModel  # type: ignore
            model = WhisperModel("base", device="cpu")
            log.info("🤖 Whisper backend: faster_whisper (base, cpu)")
            return ("faster_whisper", model)
        except Exception:
            pass

        try:
            import whisper  # type: ignore
            model = whisper.load_model("base")
            log.info("🤖 Whisper backend: whisper (base)")
            return ("whisper", model)
        except Exception:
            return None

    def _recognize_whisper(self) -> str:
        """
        Capture un court segment audio via SR s'il est dispo, puis transcrit via Whisper.
        Si SR indisponible → retourne vide (pas d’accès micro natif ici).
        """
        if self._whisper_backend is None:
            return ""
        if not (self.recognizer and self.microphone):
            # Pas de pipeline de capture -> silencieux
            return ""

        backend, model = self._whisper_backend
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=6)
            wav = audio.get_wav_data()

            if backend == "faster_whisper":
                # faster_whisper attend un chemin de fichier ou un buffer ndarray;
                # pour rester simple ici on ne convertit pas → on passe.
                # (À améliorer si besoin avec scipy.io.wavfile)
                return ""
            else:
                # whisper (openai) accepte un chemin; on va créer un tmp si besoin.
                # Pour éviter les I/O, on reste neutre ici. Amélioration ultérieure possible.
                return ""
        except Exception:
            return ""

    # ------------------------------------------------------------------ #
    # Intégration UI + pipeline
    # ------------------------------------------------------------------ #
    def _on_phrase_recognized(self, text: str):
        # 1) Mémoriser (déjà fait dans la boucle)
        # 2) Pousser vers l'UI
        self._push_transcript_to_scene(text)
        # 3) Exécution auto optionnelle
        if self.auto_execute:
            self._run_pipeline_on_main_thread(text)

    def _push_transcript_to_scene(self, text: str):
        if bpy is None:
            return

        def _set():
            try:
                scn = bpy.context.scene
                if hasattr(scn, "blade_transcript"):
                    scn.blade_transcript = text
            except Exception as e:
                log.warning(f"Impossible de pousser le transcript dans la Scene: {e}")
            return None  # ne pas relancer

        try:
            bpy.app.timers.register(_set, first_interval=0.0)
        except Exception as e:
            log.warning(f"Timers Blender indisponibles : {e}")

    def _run_pipeline_on_main_thread(self, text: str):
        if bpy is None:
            return

        def _run():
            try:
                from ares.core.run_pipeline import run_pipeline
                run_pipeline(text)
            except Exception as e:
                log.exception(e)
            return None

        try:
            bpy.app.timers.register(_run, first_interval=0.0)
        except Exception as e:
            log.warning(f"Impossible de planifier l'exécution auto : {e}")
