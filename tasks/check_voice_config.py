# tasks/check_voice_config.py

"""
Vérifie la validité de voice_config.yaml : structure, doublons, intents sans phrase ou nom
Affiche un résumé clair des problèmes trouvés
"""

import os

import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "ares", "config", "voice_config.yaml")


def check_yaml():
    if not os.path.exists(CONFIG_PATH):
        print("❌ Fichier voice_config.yaml introuvable.")
        return

    with open(CONFIG_PATH, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        print("❌ Format invalide : voice_config.yaml doit contenir une liste.")
        return

    seen_names = set()
    errors = 0

    for idx, intent in enumerate(data):
        name = intent.get("name")
        phrase = intent.get("phrase")

        if not name or not phrase:
            print(f"⚠️  Intent incomplet à l'index {idx} : name={name}, phrase={phrase}")
            errors += 1
        elif name in seen_names:
            print(f"⚠️  Doublon de nom d'intent : {name}")
            errors += 1
        else:
            seen_names.add(name)

    print(f"✅ Vérification terminée. {len(data)} intents chargés, {errors} problèmes trouvés.")


if __name__ == '__main__':
    check_yaml()
