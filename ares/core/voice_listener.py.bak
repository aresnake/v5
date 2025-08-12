# ares/core/voice_listener.py

"""
VoiceListener â€“ Ã‰coute et transcrit la voix utilisateur en temps rÃ©el
Utilise la lib SpeechRecognition pour capter le micro et envoyer la phrase
"""

import speech_recognition as sr
from ares.core.logger import get_logger
from ares.core.run_pipeline import main as run_pipeline

log = get_logger("VoiceListener")
recognizer = sr.Recognizer()
micro = sr.Microphone()


def listen_once():
    """
    Lance une Ã©coute unique, retourne la phrase reconnue (ou None).
    """
    with micro as source:
        log.info("ðŸŽ¤ PrÃªte Ã  Ã©couter...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        phrase = recognizer.recognize_google(audio, language="fr-FR")
        log.info(f"ðŸ—£ Phrase reconnue : {phrase}")
        return phrase
    except sr.UnknownValueError:
        log.warning("â“ Audio incomprÃ©hensible.")
    except sr.RequestError as e:
        log.error(f"âŒ Erreur de reconnaissance : {e}")

    return None


def start_voice_loop():
    """
    Lance une boucle d'Ã©coute continue. Utilisable dans un thread ou modal.
    """
    log.info("ðŸ” Boucle d'Ã©coute vocale dÃ©marrÃ©e.")
    while True:
        phrase = listen_once()
        if phrase:
            run_pipeline(phrase, mode="voice")
