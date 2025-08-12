# ares/bots/routine_tracker.py

"""
RoutineTracker â€“ Enregistre les intents exÃ©cutÃ©s pour dÃ©tecter des sÃ©quences rÃ©currentes (routines potentielles).
Les sÃ©quences sont stockÃ©es dans routine_history.json
"""

import json
import os
from datetime import datetime

from ares.core.logger import get_logger

ROUTINE_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "routine_history.json")
log = get_logger("RoutineTracker")

os.makedirs(os.path.dirname(ROUTINE_PATH), exist_ok=True)


def log_intent(intent_name):
    timestamp = datetime.now().isoformat()
    entry = {"name": intent_name, "timestamp": timestamp}

    history = []
    if os.path.exists(ROUTINE_PATH):
        with open(ROUTINE_PATH, encoding="utf-8") as f:
            history = json.load(f)

    history.append(entry)

    with open(ROUTINE_PATH, "w", encoding="utf-8") as f:
        json.dump(history[-100:], f, indent=2, ensure_ascii=False)  # garde les 100 derniers

    log.debug(f"ðŸ“Œ Intent loggÃ© pour routine : {intent_name}")
