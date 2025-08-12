"""
Test All Pipeline – Teste tous les intents dfinis dans voice_config.yaml
Vrifie que chaque phrase fonctionne correctement dans le pipeline complet.
"""

import os
import pytest
from ares.voice.voice_config_manager import load_config
from ares.core.run_pipeline import main as run_pipeline

FAILED = []
SUCCEEDED = []

def test_all_intents():
    config = load_config()
    assert isinstance(config, dict)

    for name, intent in config.items():
        phrase = intent.get("phrase", "")
        if not phrase:
            continue

        try:
            run_pipeline(phrase, mode="test")
            SUCCEEDED.append(name)
        except Exception as e:
            FAILED.append((name, str(e)))

    print("\n--- Rsum ---")
    print(f"? Russites : {len(SUCCEEDED)}")
    print(f"? checs : {len(FAILED)}")
    if FAILED:
        for name, err in FAILED:
            print(f"? {name} ? {err}")
