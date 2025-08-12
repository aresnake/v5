# ares/tools/routine_suggester.py

"""
RoutineSuggester â€“ DÃ©tecte les routines d'intents rÃ©currentes Ã  partir de routine_history.json
GÃ©nÃ¨re des blocs de routines proposÃ©s (futurs super-intents)
"""

import os
import json
from collections import Counter
from ares.core.logger import get_logger

ROUTINE_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "routine_history.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "routines_suggested.yaml")

log = get_logger("RoutineSuggester")

def extract_sequences(history, window=3):
    names = [item["name"] for item in history if "name" in item]
    sequences = [tuple(names[i:i+window]) for i in range(len(names) - window + 1)]
    return sequences

def run():
    if not os.path.exists(ROUTINE_PATH):
        log.warning("Aucune routine enregistrÃ©e.")
        return

    with open(ROUTINE_PATH, encoding="utf-8") as f:
        history = json.load(f)

    sequences = extract_sequences(history)
    counter = Counter(sequences)
    top = counter.most_common(5)

    routines = []
    for idx, (seq, freq) in enumerate(top):
        routines.append({
            "name": f"routine_auto_{idx+1}",
            "description": f"Routine frÃ©quente dÃ©tectÃ©e ({freq}x)",
            "sequence": list(seq),
            "tags": ["auto", "suggestion"]
        })

    if routines:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            import yaml
            yaml.dump(routines, f, allow_unicode=True, sort_keys=False)
        log.info(f"âœ… {len(routines)} routines suggÃ©rÃ©es dans : {OUTPUT_PATH}")
    else:
        log.info("Aucune routine significative dÃ©tectÃ©e.")

if __name__ == "__main__":
    run()
