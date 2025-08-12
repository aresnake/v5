# ares/tools/validate_suggestions.py

"""
validate_suggestions.py â€“ Permet de valider ou rejeter les suggestions de config/suggestions_pending.yaml
Les suggestions validÃ©es sont injectÃ©es dans voice_config.yaml
"""

import os
import yaml
from ares.core.logger import get_logger
from ares.tools.utils_yaml import load_yaml, save_yaml

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "config")
VOICE_CONFIG_PATH = os.path.join(CONFIG_DIR, "voice_config.yaml")
PENDING_PATH = os.path.join(CONFIG_DIR, "suggestions_pending.yaml")

log = get_logger("SuggestionValidator")

def validate_all():
    pending = load_yaml(PENDING_PATH)
    if not pending or not isinstance(pending, list):
        log.warning("âŒ Aucune suggestion Ã  valider.")
        return

    config = load_yaml(VOICE_CONFIG_PATH)
    if not config or not isinstance(config, list):
        config = []

    existing_names = {entry.get("name") for entry in config}
    added = 0

    for suggestion in pending:
        name = suggestion.get("name")
        if name and name not in existing_names:
            config.append(suggestion)
            added += 1

    if added:
        save_yaml(VOICE_CONFIG_PATH, config)
        log.info(f"âœ… {added} suggestions injectÃ©es dans voice_config.yaml")
    else:
        log.info("ðŸ” Aucune suggestion nouvelle Ã  injecter.")

    # Nettoyage
    os.remove(PENDING_PATH)
    log.info("ðŸ—‘ï¸ suggestions_pending.yaml supprimÃ©")

if __name__ == "__main__":
    validate_all()
