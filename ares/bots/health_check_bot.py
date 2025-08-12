# ares/bots/health_check_bot.py

import os
import importlib
from ares.core.logger import get_logger
from ares.tools.utils_yaml import load_yaml

SUMMARY_PATH = os.path.join("summary", "health_check.txt")
CONFIG_PATH = os.path.join("ares", "config", "voice_config.yaml")
REQUIRED_MODULES = [
    "ares.core.run_pipeline",
    "ares.tools.intent_resolver",
    "ares.bots.injector_bot",
]

log = get_logger("HealthCheck")

def check_voice_config_format():
    try:
        config = load_yaml(CONFIG_PATH)
        if not isinstance(config, list):
            return "âŒ voice_config.yaml n'est pas une liste"
        elif not config:
            return "âš ï¸ voice_config.yaml est vide"
        else:
            return f"âœ… {len(config)} intents chargÃ©s"
    except Exception as e:
        return f"âŒ Erreur chargement YAML : {e}"

def check_module_imports():
    results = []
    for module_path in REQUIRED_MODULES:
        try:
            importlib.import_module(module_path)
            results.append(f"âœ… Import {module_path}")
        except Exception as e:
            results.append(f"âŒ Import {module_path} Ã©chouÃ© : {e}")
    return results

def run_health_check():
    os.makedirs("summary", exist_ok=True)
    results = []

    results.append("ðŸ©º BLADE Health Check Report\n----------------------------")
    results.append(check_voice_config_format())
    results += check_module_imports()

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    for line in results:
        print(line)

if __name__ == "__main__":
    run_health_check()
