# ares/tools/routine_executor.py

"""
RoutineExecutor – Exécute une routine validée (liste d'intents) depuis routines_validated.yaml
"""

import os

import yaml

from ares.core.logger import get_logger
from ares.core.run_pipeline import main as run_pipeline

ROUTINES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "routines_validated.yaml")
VOICE_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "voice_config.yaml")

log = get_logger("RoutineExecutor")


def load_yaml_list(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except Exception as e:
        log.error(f"Erreur lecture {path} : {e}")
        return []


def execute_routine(routine_name: str):
    routines = load_yaml_list(ROUTINES_PATH)
    config = load_yaml_list(VOICE_CONFIG)

    target = next((r for r in routines if r.get("name") == routine_name), None)
    if not target:
        log.error(f"Routine '{routine_name}' introuvable.")
        return

    sequence = target.get("sequence", [])
    if not sequence:
        log.warning(f"Routine '{routine_name}' vide.")
        return

    name_to_phrase = {
        entry.get("name"): entry.get("phrase")
        for entry in config
        if entry.get("name") and entry.get("phrase")
    }

    for intent_name in sequence:
        phrase = name_to_phrase.get(intent_name)
        if phrase:
            log.info(f"?? Exécution : {intent_name} via '{phrase}'")
            run_pipeline(phrase)
        else:
            log.warning(f"? Phrase introuvable pour intent : {intent_name}")


if __name__ == "__main__":
    execute_routine("routine_auto_1")
