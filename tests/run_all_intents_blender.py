import importlib
import os
import shutil

import yaml


#  Nettoyage automatique des __pycache__ dans tout le projet
def clear_pycache(base_path):
    for root, dirs, _files in os.walk(base_path):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)


clear_pycache(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# â€ Recharge force du resolver corrig
import ares.tools.intent_resolver as resolver

importlib.reload(resolver)

#  Injection dans le pipeline
from ares import tools

tools.intent_resolver = resolver

from ares.core.run_pipeline import main as run_pipeline
from ares.logger import get_logger

log = get_logger("BlenderIntentRunner")


def resolve_config_path():
    candidates = [
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "config", "voice_config.yaml")
        ),
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "config", "voice_config.yaml")
        ),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Aucun fichier voice_config.yaml trouv.")


def load_yaml_config(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    log.info(" Lancement des tests vocaux Blender (background)")
    config_path = resolve_config_path()
    config = load_yaml_config(config_path)

    phrases = [
        block["phrase"]
        for block in config.values()
        if isinstance(block, dict) and "phrase" in block
    ]
    for phrase in phrases:
        log.info(f"â€ Test de la phrase : {phrase}")
        result = run_pipeline(phrase, mode="test")
        log.info(f"â€œ Rsultat : {result}")


if __name__ == "__main__":
    main()
