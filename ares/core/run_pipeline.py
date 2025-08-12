# ares/core/run_pipeline.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
import traceback
from typing import Optional, Dict, Any

from ares.core.intent_parser import parse_intent
from ares.core.logger import get_logger

# Bots (optionnels) : on protège les imports pour ne jamais bloquer la pipeline.
try:
    from ares.bots.session_log_enricher_bot import enrich_log  # type: ignore
except Exception:  # pragma: no cover
    enrich_log = None  # type: ignore

try:
    from ares.bots.injector_bot import inject_intents_into_pending  # type: ignore
except Exception:  # pragma: no cover
    inject_intents_into_pending = None  # type: ignore

# Pipeline Manager (optionnel mais recommandé)
try:
    from ares.core.pipeline_manager import run_with_manager  # type: ignore
except Exception:  # pragma: no cover
    run_with_manager = None  # type: ignore

# Fallback direct si le manager est indisponible
try:
    from ares.tools.intent_executor import execute_intent  # type: ignore
except Exception:  # pragma: no cover
    execute_intent = None  # type: ignore

log = get_logger("RunPipeline")


def main(
    phrase: Optional[str] = None,
    mode: str = "voice",
    *,
    allow_injection: bool = True,
    dry_run: bool = False,
    preparsed_intent: Optional[Dict[str, Any]] = None,
    use_pipeline_manager: bool = True,
) -> bool:
    """
    Lance la pipeline principale Blade.

    Étapes :
      1) Parse la phrase (ou utilise `preparsed_intent` si fourni)
      2) Enrichit le log (si bot dispo)
      3) Injecte l'intent dans les "pending" si nouveau (si bot dispo & allow_injection)
      4) Exécute l'intent (sauf en dry_run), via Pipeline Manager si dispo, sinon fallback direct.

    Args:
        phrase: texte à interpréter (ignoré si `preparsed_intent` est fourni)
        mode: 'voice', 'text', 'ui', etc. (transmis au bot d'enrichissement)
        allow_injection: True pour autoriser l'injection dans les pending
        dry_run: True pour ne pas exécuter l'intent (parse + bots seulement)
        preparsed_intent: dict d’intent déjà prêt (bypass parse)
        use_pipeline_manager: True pour router via Pipeline Manager si dispo

    Returns:
        bool: True si tout s'est bien passé (ou si dry_run a réussi), False sinon.
    """
    t0 = time.perf_counter()
    log.info("🚀 Lancement de la pipeline Blade…")

    # ---------------------------
    # 1) Résolution de l'intent
    # ---------------------------
    intent: Optional[Dict[str, Any]] = None

    if preparsed_intent is not None:
        if not isinstance(preparsed_intent, dict):
            log.error("❌ 'preparsed_intent' doit être un dict.")
            return False
        intent = dict(preparsed_intent)  # shallow copy
        log.info("🧩 Intent pré-parsé reçu (bypass parse_intent).")

    else:
        if not phrase or not str(phrase).strip():
            log.warning("🛑 Aucune phrase reçue.")
            return False

        log.info(f"🗣️ Phrase reçue : {phrase}")
        try:
            intent = parse_intent(phrase)
        except Exception as e:
            log.error(f"❌ Exception pendant parse_intent : {e}")
            log.debug("".join(traceback.format_exc()))
            intent = None

    if not intent:
        log.warning("❓ Aucun intent détecté.")
        return False

    # Standardisation minimale (sécurité)
    intent.setdefault("name", intent.get("id") or "intent_sans_nom")
    intent.setdefault("params", intent.get("params", {}) or {})
    name = intent.get("name")
    operator = intent.get("operator")

    log.info(f"🎯 Intent détecté : {name} | operator={operator}")

    if not operator:
        log.error("❌ Intent sans opérateur : exécution impossible.")
        return False

    # ---------------------------
    # 2) Enrichissement du log
    # ---------------------------
    try:
        if enrich_log is not None:
            enrich_log(intent, mode=mode)
            log.info("🧾 Log enrichi avec succès.")
        else:
            log.debug("ℹ️ Bot 'session_log_enricher_bot' indisponible, étape ignorée.")
    except Exception as e:  # ne doit pas casser la pipeline
        log.warning(f"⚠️ Échec enrichissement log : {e}")
        log.debug("".join(traceback.format_exc()))

    # ---------------------------
    # 3) Injection en pending
    # ---------------------------
    try:
        if allow_injection and inject_intents_into_pending is not None:
            inject_intents_into_pending([intent])
            log.info("📥 Intent injecté (pending) si nouveau.")
        else:
            if not allow_injection:
                log.debug("ℹ️ Injection désactivée (allow_injection=False).")
            else:
                log.debug("ℹ️ Bot 'injector_bot' indisponible, étape ignorée.")
    except Exception as e:  # ne doit pas casser la pipeline
        log.warning(f"⚠️ Échec injection pending : {e}")
        log.debug("".join(traceback.format_exc()))

    # ---------------------------
    # 4) Exécution
    # ---------------------------
    if dry_run:
        dt = (time.perf_counter() - t0) * 1000.0
        log.info(f"🧪 Dry-run activé : exécution sautée (parse/log/injection uniquement). ({dt:.1f} ms)")
        return True

    try:
        # Route via Pipeline Manager si demandé et disponible, sinon fallback direct.
        if use_pipeline_manager and run_with_manager is not None:
            success = run_with_manager(intent)
        else:
            if execute_intent is None:
                log.error("❌ Aucun exécuteur disponible (ni Pipeline Manager, ni execute_intent).")
                return False
            success = execute_intent(intent)

        if not success:
            log.error("❌ Échec lors de l'exécution de l'intent.")
            return False

        dt = (time.perf_counter() - t0) * 1000.0
        log.info(f"✅ Pipeline terminée avec succès. ({dt:.1f} ms)")
        return True

    except Exception as e:
        log.error(f"💥 Exception dans run_pipeline lors de l'exécution : {e}")
        log.debug("".join(traceback.format_exc()))
        return False


# Alias historique si d'autres modules appellent run_pipeline(text)
def run_pipeline(phrase: Optional[str] = None, mode: str = "voice") -> bool:
    """Alias rétro‑compatible."""
    return main(phrase=phrase, mode=mode)
