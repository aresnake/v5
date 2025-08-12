# ares/datasets/session_dataset.py

"""
SessionDataset â€“ GÃ¨re l'enregistrement passif des actions utilisateur
UtilisÃ© par l'agent passif pour construire un historique persistent de comportements
"""

import os
import json
import uuid
from datetime import datetime
from ares.core.logger import get_logger

log = get_logger("SessionDataset")
DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")
os.makedirs(DATASET_DIR, exist_ok=True)

class SessionDataset:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        self.actions = []

    def log_action(self, action: dict):
        self.actions.append(action)
        log.debug(f"ðŸ§  Action ajoutÃ©e au dataset : {action}")

    def save(self):
        path = os.path.join(DATASET_DIR, f"session_{self.session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"session_id": self.session_id, "actions": self.actions}, f, indent=2)

        log.info(f"ðŸ’¾ Dataset utilisateur sauvegardÃ© : {path}")
