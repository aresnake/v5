# ares/core/pipeline_manager.py
from __future__ import annotations
from typing import Dict, Any, List
from ares.core.logger import get_logger
from ares.pipelines.base import PipelineBase
from ares.pipelines.default import DefaultPipeline
from ares.pipelines.render import RenderPipeline
from ares.pipelines.material import MaterialPipeline

log = get_logger("PipelineManager")

class PipelineManager:
    def __init__(self) -> None:
        self._pipelines: List[PipelineBase] = [
            # ordre = priorité
            RenderPipeline(),
            MaterialPipeline(),
            DefaultPipeline(),
        ]

    def select(self, intent: Dict[str, Any]) -> PipelineBase:
        for pipe in self._pipelines:
            try:
                if pipe.match(intent):
                    return pipe
            except Exception as e:
                log.warning(f"Match échoué sur {pipe.name}: {e}")
        return DefaultPipeline()

    def run(self, intent: Dict[str, Any]) -> bool:
        pipe = self.select(intent)
        log.info(f"▶️ Pipeline sélectionnée: {pipe.name}")
        return pipe.run(intent)

# singleton simple
_manager = PipelineManager()

def run_with_manager(intent: Dict[str, Any]) -> bool:
    return _manager.run(intent)
