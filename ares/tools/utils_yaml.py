# ares/tools/utils_yaml.py

import os

import yaml


def load_yaml(path):
    """Load YAML; return [] if missing or invalid."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data is not None else []
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement YAML : {e}")
        return []


def save_yaml(path, data):
    """Save YAML; create parent dirs if needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    except Exception as e:
        print(f"⚠️ Erreur lors de l'enregistrement YAML : {e}")
