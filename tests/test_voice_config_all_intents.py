# tests/test_voice_config_all_intents.py

import os
import time
from datetime import datetime
from ares.core.run_pipeline import main as run_pipeline
from ares.tools.utils_yaml import load_yaml

CONFIG_PATH = os.path.join("ares", "config", "voice_config.yaml")
SUMMARY_DIR = os.path.join("summary")
SUMMARY_PATH = os.path.join(SUMMARY_DIR, "test_voice_results.txt")

os.makedirs(SUMMARY_DIR, exist_ok=True)

def log_result(lines):
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def test_all_intents():
    intents = load_yaml(CONFIG_PATH)
    if not isinstance(intents, list):
        print("❌ Le fichier voice_config.yaml n'est pas une liste valide.")
        return

    results = []
    ok, fail, skipped = 0, 0, 0

    for intent in intents:
        phrase = intent.get("phrase")
        name = intent.get("name")
        if not phrase:
            results.append(f"⏩ Intent sans phrase : {name}")
            skipped += 1
            continue

        print(f"▶️ Test : {phrase}")
        try:
            result = run_pipeline(phrase)
            if result:
                results.append(f"✅ {phrase} → {name}")
                ok += 1
            else:
                results.append(f"❌ {phrase} → intent non exécuté")
                fail += 1
        except Exception as e:
            results.append(f"💥 {phrase} → Exception : {e}")
            fail += 1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = [
        f"🧪 Résultats du test complet ({timestamp})",
        f"✔️ Succès : {ok}",
        f"❌ Échecs : {fail}",
        f"⏩ Ignorés : {skipped}",
        "-" * 40
    ]
    all_lines = header + results
    log_result(all_lines)

    print("\n".join(header))

if __name__ == "__main__":
    test_all_intents()
