"""
Test Voice Config – checs
Rapport texte complet des erreurs d’intents (hors Blender si besoin).
"""

import os
from ares.voice.voice_config_manager import load_config
from ares.core.run_pipeline import main as run_pipeline

FAILED = []

def test_all_intents():
    config = load_config()
    assert isinstance(config, dict)

    for name, intent in config.items():
        phrase = intent.get("phrase", "")
        if not phrase:
            continue

        try:
            run_pipeline(phrase, mode="test")
        except Exception as e:
            FAILED.append((name, str(e)))

    if FAILED:
        summary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "summary", "failed_intents.txt"))
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            for name, err in FAILED:
                f.write(f"{name}: {err}\n")

        print(f"\n? {len(FAILED)} intents en erreur ? summary/failed_intents.txt")
    else:
        print("\n? Tous les intents ont russi.")
