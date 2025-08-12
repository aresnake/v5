# ares/bots/injector_bot.py

import os
from datetime import datetime

from ares.core.logger import get_logger
from ares.tools.utils_yaml import load_yaml, save_yaml

log = get_logger("InjectorBot")

CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))
VOICE_CONFIG = os.path.join(CONFIG_DIR, "voice_config.yaml")  # ðŸ”’ Lecture seule
PENDING_PATH = os.path.join(CONFIG_DIR, "intents_pending.yaml")  # ðŸ“ Cible d'injection


def inject_intents_into_pending(new_intents: list):
    """
    Injecte des intents dans intents_pending.yaml si absents dans voice_config.yaml.
    """
    log.info(f"ðŸ“¥ Injection de {len(new_intents)} intents...")

    existing = load_yaml(VOICE_CONFIG)
    pending = load_yaml(PENDING_PATH)

    if not isinstance(existing, list):
        log.warning("âš ï¸ voice_config.yaml invalide (non-liste). Lecture uniquement.")
        existing = []

    if not isinstance(pending, list):
        pending = []

    existing_names = {entry.get("name") for entry in existing}
    pending_names = {entry.get("name") for entry in pending}
    injected_count = 0

    for new in new_intents:
        name = new.get("name") or new.get("intent")
        _phrase = new.get("phrase")  # kept for debug
        if not name or name in existing_names or name in pending_names:
            continue

        enriched = {
            **new,
            "intent": name,
            "source": "auto_injector",
            "injected_at": datetime.now().isoformat(timespec="seconds"),
        }
        pending.append(enriched)
        injected_count += 1

    if injected_count > 0:
        save_yaml(PENDING_PATH, pending)
        log.info(f"âœ… {injected_count} intents ajoutÃ©s Ã  intents_pending.yaml")
    else:
        log.info("ðŸ“Ž Aucun nouvel intent injectÃ©.")
