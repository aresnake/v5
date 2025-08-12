# ares/agents/agent_codex.py

"""
CodexAgent â€“ Analyse les erreurs d'intents et propose des corrections via LLM
Peut Ãªtre connectÃ© Ã  GPT, Gemini ou un modÃ¨le local
"""

from ares.core.logger import get_logger

log = get_logger("CodexAgent")

class CodexAgent:
    def __init__(self):
        self.failures = []

    def prepare(self):
        log.info("ðŸ¤– CodexAgent prÃªt Ã  analyser les Ã©checs.")

    def log_failure(self, phrase: str, error: str):
        self.failures.append({"phrase": phrase, "error": error})
        log.warning(f"âš ï¸ Intent Ã©chouÃ© : '{phrase}' | erreur : {error}")

    def analyze_failures(self):
        if not self.failures:
            log.info("âœ… Aucun Ã©chec Ã  analyser.")
            return []

        log.info(f"ðŸ“Š Analyse de {len(self.failures)} intents en Ã©chec...")
        suggestions = []

        for fail in self.failures:
            phrase = fail['phrase']
            error = fail['error']
            suggestion = f"Corriger '{phrase}' â†’ cause probable : {error}"
            suggestions.append(suggestion)
            log.info(f"ðŸ’¡ Suggestion : {suggestion}")

        return suggestions
