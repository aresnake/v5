"""
Test VoiceConfigManager â€“ Vrifie le chargement du YAML vocal
"""

from ares.voice.voice_config_manager import load_config


def test_yaml_loads_correctly():
    config = load_config()
    assert isinstance(config, dict)
    assert len(config) > 0

    for _intent_name, intent in config.items():
        assert "phrase" in intent
        assert "operator" in intent
        assert isinstance(intent["phrase"], str)
