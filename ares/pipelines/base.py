# ares/pipelines/base.py
from __future__ import annotations

from typing import Any


class PipelineBase:
    """Contrat minimal pour une mini‑pipeline."""

    name = "base"

    def match(self, intent: dict[str, Any]) -> bool:
        """Retourne True si cette pipeline sait gérer l'intent."""
        return False

    def run(self, intent: dict[str, Any]) -> bool:
        """Exécute l'intent (peut appeler execute_intent ou steps custom)."""
        raise NotImplementedError
