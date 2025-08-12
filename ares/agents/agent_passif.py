# ares/agents/agent_passif.py

"""
PassiveAgent – Agent passif de Blade
Observe les actions Blender et suggère des routines/intents à partir du comportement utilisateur
"""

from ares.core.logger import get_logger

log = get_logger("PassiveAgent")


class PassiveAgent:
    def __init__(self):
        self.active = False
        self.history = []

    def start(self):
        self.active = True
        self.history.clear()
        log.info("?? PassiveAgent activé. Observation des actions utilisateur...")

    def stop(self):
        self.active = False
        log.info("?? PassiveAgent désactivé.")

    def record_action(self, action: str):
        """
        Enregistre une action utilisateur (via editor_watcher ou autre hook)
        """
        if not self.active:
            return
        self.history.append(action)
        log.debug(f"??? Action observée : {action}")

    def suggest_intents(self) -> list[str]:
        """
        Génère des suggestions d'intents basées sur les actions passées
        """
        return []


# ?? Points d’entrée pour register/unregister
_passive_agent = PassiveAgent()


def activate_passive_agent():
    _passive_agent.start()


def deactivate_passive_agent():
    _passive_agent.stop()
