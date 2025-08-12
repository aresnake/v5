import os
import yaml
from ares.core.logger import get_logger

log = get_logger("VoiceConfigManager")

def get_voice_config_path():
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(base_path, "..", "config", "voice_config.yaml"))
    return config_path

VOICE_CONFIG_PATH = get_voice_config_path()

def load_config():
    try:
        with open(VOICE_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        log.info(f"ðŸ“„ voice_config.yaml chargÃ© depuis {VOICE_CONFIG_PATH}")
        return config or {}
    except Exception as e:
        log.error(f"âŒ Erreur de chargement voice_config.yaml : {e}")
        return {}
