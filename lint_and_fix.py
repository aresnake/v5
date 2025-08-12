# lint_and_fix.py – Nettoyeur automatique pour Blade v5.1

"""
Ce script :
- détecte et corrige les imports cassés (ex: )
- remplace les caractères unicode illisibles (ex: même → même)
- vérifie que tous les fichiers sont bien en utf-8
"""

import os
import re

ROOT = os.path.dirname(__file__)
TARGET_EXT = ".py"

REPLACEMENTS = [
    (
        r"from ares.voice.voice_config_manager import load_config",
        "from ares.voice.voice_config_manager import load_config",
    ),
    (r"", ""),
    (r"même", "même"),
    (r"raise ImportError\(f\?", "raise ImportError(f\"❌"),
]


def fix_file(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    original = content
    for pattern, repl in REPLACEMENTS:
        content = re.sub(pattern, repl, content)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Corrigé : {path}")


def run():
    for root, _, files in os.walk(ROOT):
        for file in files:
            if file.endswith(TARGET_EXT):
                fix_file(os.path.join(root, file))


if __name__ == "__main__":
    run()
