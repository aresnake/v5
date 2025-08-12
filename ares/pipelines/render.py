# ares/pipelines/render.py
from __future__ import annotations

from typing import Any

from ares.core.logger import get_logger
from ares.pipelines.base import PipelineBase

# from ares.tools.render_video import quick_render_mp4  # à brancher quand prêt
from ares.tools.intent_executor import execute_intent

log = get_logger("RenderPipeline")


class RenderPipeline(PipelineBase):
    name = "render"

    def match(self, intent: dict[str, Any]) -> bool:
        domain = (intent.get("domain") or "").lower()
        tags = {t.lower() for t in (intent.get("tags") or [])}
        op = (intent.get("operator") or "").lower()
        return (
            domain == "render" or "render" in tags or op.startswith("render.")  # ex: render.render
        )

    def run(self, intent: dict[str, Any]) -> bool:
        # Ici, tu pourras faire: préparation scène, config FFmpeg, etc.
        # if intent["name"] == "rendu_mp4_rapide":
        #     return quick_render_mp4(**intent.get("params", {}))
        return execute_intent(intent)
