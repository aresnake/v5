# ares/tools/suggestions_pending_generator.py

"""
Ce script lit tous les fichiers codex_prompts/from_passive/*.yaml
et regroupe les suggestions dans config/suggestions_pending.yaml
"""

import os

import yaml

from ares.core.logger import get_logger

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "codex_prompts", "from_passive")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "suggestions_pending.yaml")

log = get_logger("SuggestionCollector")

seen = set()
suggestions = []

for file in os.listdir(PROMPT_DIR):
    if not file.endswith(".yaml"):
        continue
    path = os.path.join(PROMPT_DIR, file)
    with open(path, encoding="utf-8") as f:
        block = yaml.safe_load(f)
        if isinstance(block, list):
            for intent in block:
                name = intent.get("name")
                if name and name not in seen:
                    suggestions.append(intent)
                    seen.add(name)

if suggestions:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        yaml.dump(suggestions, f, allow_unicode=True, sort_keys=False)
    log.info(f"âœ… {len(suggestions)} suggestions enregistrÃ©es dans : {OUTPUT_PATH}")
else:
    log.warning("âŒ Aucune suggestion trouvÃ©e pour pending.yaml")
