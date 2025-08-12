# ares/pipelines/default.py
from __future__ import annotations

from typing import Any

from ares.pipelines.base import PipelineBase
from ares.tools.intent_executor import execute_intent


class DefaultPipeline(PipelineBase):
    name = "default"

    def match(self, intent: dict[str, Any]) -> bool:
        return True  # fallback

    def run(self, intent: dict[str, Any]) -> bool:
        return execute_intent(intent)
