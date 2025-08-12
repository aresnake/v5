# ares/tools/__init__.py

try:
    from .intent_resolver import resolve_and_execute
    from .operator_classifier import classify_operator
except ImportError as e:
    from ares.core.logger import get_logger

    log = get_logger("tools/__init__")
    log.warning(f"âŒ Erreur import tools : {e}")
