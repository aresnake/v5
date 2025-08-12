# ares/codex/codex_suggester.py

"""
codex_suggester.py
Lit les résumés de sessions passives (".json") et génère des blocs d'intents YAML dans codex_prompts/from_passive/
"""

import os
import json
from datetime import datetime
from pathlib import Path
from ares.logger import get_logger

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "codex_prompts", "from_passive")
SUMMARY_DIR = os.path.join(os.path.dirname(__file__), "..", "summary")

log = get_logger("CodexSuggester")
os.makedirs(PROMPTS_DIR, exist_ok=True)

def parse_observation(action: str) -> dict:
    """
    Simule une analyse IA pour transformer une action en intent YAML.
    """
    if "cube" in action.lower():
        return {
            "name": "ajouter_cube_auto",
            "phrase": "ajoute un cube automatiquement",
            "operator": "mesh.primitive_cube_add",
            "params": {"location": [0, 0, 0]},
            "category": "auto_suggested",
            "source": "passive_agent",
            "tags": ["auto", "suggestion"]
        }
    return None

def generate_prompt_from_summary(summary_file):
    with open(summary_file, encoding="utf-8") as f:
        data = json.load(f)

    session_id = data.get("session", "unknown")
    results = data.get("results", [])

    suggestions = []
    for phrase, status in results:
        if status == "observed":
            suggestion = parse_observation(phrase)
            if suggestion:
                suggestions.append(suggestion)

    if not suggestions:
        log.info(f"❌ Aucune suggestion d'intent trouvée pour {session_id}.")
        return

    output_path = os.path.join(PROMPTS_DIR, f"{session_id}.yaml")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Suggestions d'intents pour session : {session_id}\n\n")
        for intent in suggestions:
            f.write("- name: " + intent["name"] + "\n")
            f.write("  phrase: " + intent["phrase"] + "\n")
            f.write("  operator: " + intent["operator"] + "\n")
            f.write("  params:\n")
            for k, v in intent["params"].items():
                f.write(f"    {k}: {v}\n")
            f.write("  category: " + intent["category"] + "\n")
            f.write("  source: " + intent["source"] + "\n")
            f.write("  tags: [" + ", ".join(intent["tags"]) + "]\n\n")

    log.info(f"✅ Prompt Codex généré : {output_path}")

def run():
    for file in os.listdir(SUMMARY_DIR):
        if file.startswith("session_") and file.endswith(".json"):
            path = os.path.join(SUMMARY_DIR, file)
            generate_prompt_from_summary(path)

if __name__ == "__main__":
    run()
