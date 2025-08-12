# ares/codex/generate_learning_prompts.py

"""
Transforme les fichiers summary/session_*.json en prompts Codex d'apprentissage dans codex_prompts/for_learning/
"""

import json
import os
from datetime import datetime

from ares.logger import get_logger

SUMMARY_DIR = os.path.join(os.path.dirname(__file__), "..", "summary")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "codex_prompts", "for_learning")

log = get_logger("LearningPrompts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_prompt(session_id, data):
    results = data.get("results", [])
    total = data.get("total_count", len(results))
    observed = [r for r in results if r[1] == "observed"]
    failed = [r for r in results if r[1] == "failed"]

    lines = [f"# Codex learning prompt – session: {session_id}", ""]
    lines.append(f"session_id: {session_id}")
    lines.append(f"timestamp: {datetime.now().isoformat()}")
    lines.append(f"total_actions: {total}")
    lines.append(f"observed_count: {len(observed)}")
    lines.append(f"failed_count: {len(failed)}")
    lines.append("")

    if observed:
        lines.append("observed_actions:")
        for obs in observed:
            lines.append(f"  - phrase: '{obs[0]}'")
        lines.append("")

    if failed:
        lines.append("failed_actions:")
        for fail in failed:
            lines.append(f"  - phrase: '{fail[0]}'")
        lines.append("")

    lines.append("learning_objectives:")
    lines.append("  - détecter des patterns répétitifs dans les actions utilisateur")
    lines.append("  - suggérer des intents vocaux équivalents")
    lines.append("  - regrouper les actions similaires en routines")

    return "\n".join(lines)


def run():
    for file in os.listdir(SUMMARY_DIR):
        if file.startswith("session_") and file.endswith(".json"):
            path = os.path.join(SUMMARY_DIR, file)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            session_id = data.get("session", file.replace("session_", "").replace(".json", ""))
            output_path = os.path.join(OUTPUT_DIR, f"{session_id}.yaml")
            prompt = build_prompt(session_id, data)

            with open(output_path, "w", encoding="utf-8") as out:
                out.write(prompt)

            log.info(f"📘 Prompt d'apprentissage généré : {output_path}")


if __name__ == "__main__":
    run()
