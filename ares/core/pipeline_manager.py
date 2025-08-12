# ares/core/pipeline_manager.py
from __future__ import annotations

from typing import Any

from ares.core.logger import get_logger
from ares.pipelines.base import PipelineBase
from ares.pipelines.default import DefaultPipeline
from ares.pipelines.material import MaterialPipeline
from ares.pipelines.render import RenderPipeline

log = get_logger("PipelineManager")


class PipelineManager:
    def __init__(self) -> None:
        self._pipelines: list[PipelineBase] = [
            # ordre = priorité
            RenderPipeline(),
            MaterialPipeline(),
            DefaultPipeline(),
        ]

    def select(self, intent: dict[str, Any]) -> PipelineBase:
        for pipe in self._pipelines:
            try:
                if pipe.match(intent):
                    return pipe
            except Exception as e:
                log.warning(f"Match échoué sur {pipe.name}: {e}")
        return DefaultPipeline()

    def run(self, intent: dict[str, Any]) -> bool:
        pipe = self.select(intent)
        log.info(f"▶️ Pipeline sélectionnée: {pipe.name}")
        return pipe.run(intent)


# singleton simple
_manager = PipelineManager()


def run_with_manager(intent: dict[str, Any]) -> bool:
    return _manager.run(intent)
