# ares/pipelines/material.py
from __future__ import annotations
from typing import Dict, Any
from ares.pipelines.base import PipelineBase
from ares.tools.intent_executor import execute_intent

class MaterialPipeline(PipelineBase):
    name = "material"

    def match(self, intent: Dict[str, Any]) -> bool:
        domain = (intent.get("domain") or "").lower()
        tags = {t.lower() for t in (intent.get("tags") or [])}
        op = (intent.get("operator") or "").lower()
        return (
            domain == "material"
            or {"material", "shader"} & tags
            or ".active_material" in op
        )

    def run(self, intent: Dict[str, Any]) -> bool:
        # Ici tu peux ajouter des steps spécifiques (création mat, nodes…)
        return execute_intent(intent)
