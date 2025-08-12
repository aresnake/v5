# ares/ui/ui_codex.py

"""
Panneau secondaire Codex – lance la pipeline IA adaptative à partir des sessions passives
Permet de relancer la génération de suggestions via Codex
"""

import os
import subprocess

import bpy

from ares.core.logger import get_logger

log = get_logger("UICodex")
BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "codex", "run_codex_pipeline.py")
)


class BLADE_PT_CodexPanel(bpy.types.Panel):
    bl_idname = "BLADE_PT_CodexPanel"
    bl_label = " Suggestions IA (Codex)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blade"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Pipeline d'adaptation Codex")
        layout.operator("blade.run_codex_pipeline", icon="FILE_REFRESH")


class BLADE_OT_RunCodexPipeline(bpy.types.Operator):
    bl_idname = "blade.run_codex_pipeline"
    bl_label = " Régénérer les suggestions IA"

    def execute(self, context):
        try:
            subprocess.run(["python", BASE_PATH], check=True)
            self.report({'INFO'}, "Pipeline Codex terminée avec succès.")
        except Exception as e:
            self.report({'ERROR'}, f"Erreur pipeline Codex : {e}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BLADE_PT_CodexPanel)
    bpy.utils.register_class(BLADE_OT_RunCodexPipeline)


def unregister():
    bpy.utils.unregister_class(BLADE_PT_CodexPanel)
    bpy.utils.unregister_class(BLADE_OT_RunCodexPipeline)
