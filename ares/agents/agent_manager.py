# ares/agents/agent_manager.py

"""
AgentManager â€“ Supervise et orchestre tous les agents internes de Blade
DÃ©marre les agents actifs, passifs, de test ou d'analyse IA (Codex).
"""

from ares.core.logger import get_logger
from ares.agents.agent_passif import PassiveAgent
from ares.agents.agent_codex import CodexAgent
from ares.agents.agent_tester import IntentTester

log = get_logger("AgentManager")

class AgentManager:
    def __init__(self):
        self.passive_agent = PassiveAgent()
        self.codex_agent = CodexAgent()
        self.tester = IntentTester()

    def start_all(self):
        log.info("ðŸš€ DÃ©marrage de tous les agents Blade...")
        self.passive_agent.start()
        self.codex_agent.prepare()
        log.info("âœ… Tous les agents ont Ã©tÃ© initialisÃ©s.")

    def run_tests(self):
        log.info("ðŸ§ª Lancement des tests d'intents...")
        self.tester.run_all_tests()

    def analyze_failures(self):
        return self.codex_agent.analyze_failures()

    def shutdown(self):
        log.info("ðŸ›‘ ArrÃªt des agents Blade...")
        self.passive_agent.stop()
