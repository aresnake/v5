# ares/agents/agent_tester.py

"""
IntentTester â€“ Lance automatiquement les tests sur tous les intents
Charge voice_config.yaml, exÃ©cute les intents et logue les rÃ©sultats
"""

import os
import yaml
from ares.core.logger import get_logger
from ares.tools.intent_executor import execute_intent
from ares.core.intent_parser import parse_intent

log = get_logger("IntentTester")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "voice_config.yaml")

class IntentTester:
    def __init__(self):
        self.results = []

    def run_all_tests(self):
        if not os.path.exists(CONFIG_PATH):
            log.error("âŒ voice_config.yaml introuvable.")
            return

        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        for intent in config:
            phrase = intent.get("phrase")
            if not phrase:
                continue

            log.info(f"ðŸ§ª Test de la phrase : {phrase}")
            detected = parse_intent(phrase)
            if not detected:
                log.warning("âš ï¸ Intent non dÃ©tectÃ©.")
                self.results.append((phrase, "not_found"))
                continue

            success = execute_intent(detected)
            status = "success" if success else "failed"
            self.results.append((phrase, status))
            log.info(f"âž¡ï¸ RÃ©sultat : {status}")
