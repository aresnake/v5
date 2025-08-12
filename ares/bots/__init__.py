# ares/bots/__init__.py

try:
    from .editor_watcher import register_handler
    from .injector_bot import inject_intents_into_pending
    from .session_log_enricher_bot import enrich_log
except ImportError as e:
    from ares.core.logger import get_logger

    log = get_logger("bots/__init__")
    log.warning(f"âŒ Erreur import bots : {e}")
