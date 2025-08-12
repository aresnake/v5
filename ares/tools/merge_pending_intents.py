# ares/tools/merge_pending_intents.py

import os
from datetime import datetime
from ares.core.logger import get_logger
from ares.tools.utils_yaml import load_yaml, save_yaml

log = get_logger("Merger")

CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))
VOICE_CONFIG = os.path.join(CONFIG_DIR, "voice_config.yaml")
PENDING_PATH = os.path.join(CONFIG_DIR, "intents_pending.yaml")

def merge_pending_intents():
    base = load_yaml(VOICE_CONFIG)
    pending = load_yaml(PENDING_PATH)

    if not isinstance(base, list):
        log.error("âŒ voice_config.yaml invalide. Annulation.")
        return

    if not isinstance(pending, list) or not pending:
        log.info("ðŸ“­ Aucun intent en attente Ã  fusionner.")
        return

    existing_names = {entry.get("name") for entry in base}
    to_add = []

    for item in pending:
        name = item.get("name") or item.get("intent")
        if not name or name in existing_names:
            continue

        clean_item = {
            "name": name,
            "phrase": item.get("phrase"),
            "operator": item.get("operator"),
            "params": item.get("params", {}),
            "category": item.get("category", "autres"),
            "description": item.get("description", ""),
            "merged_at": datetime.now().isoformat(timespec="seconds")
        }
        to_add.append(clean_item)

    if not to_add:
        log.info("ðŸ“Ž Aucun nouvel intent Ã  fusionner.")
        return

    merged = base + to_add
    save_yaml(VOICE_CONFIG, merged)
    log.info(f"âœ… {len(to_add)} intents fusionnÃ©s avec voice_config.yaml")

    # ðŸ§¹ Optionnel : vider les pending
    save_yaml(PENDING_PATH, [])
    log.info("ðŸ§¼ intents_pending.yaml vidÃ© aprÃ¨s fusion.")

if __name__ == "__main__":
    merge_pending_intents()
