# ares/ui/ui_routines.py

"""
Panneau UI – Affiche les routines suggérées automatiquement et permet de les valider
Valide dans config/routines_validated.yaml
"""

import os
import shutil

import bpy
import yaml

from ares.core.logger import get_logger

SUGGESTED_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "routines_suggested.yaml")
VALIDATED_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "routines_validated.yaml")

log = get_logger("UIRoutines")


class BLADE_PT_RoutinesPanel(bpy.types.Panel):
    bl_idname = "BLADE_PT_RoutinesPanel"
    bl_label = " Routines IA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blade"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Routines suggérées :")

        if not os.path.exists(SUGGESTED_PATH):
            layout.label(text="✓ Aucune routine suggérée.")
            return

        with open(SUGGESTED_PATH, encoding="utf-8") as f:
            routines = yaml.safe_load(f) or []

        if not routines:
            layout.label(text="✓ Liste vide.")
            return

        for routine in routines:
            layout.label(
                text=f"• {routine.get('name')} ({len(routine.get('sequence', []))} intents)"
            )

        layout.separator()
        layout.operator("blade.validate_routines", icon="CHECKMARK")


class BLADE_OT_ValidateRoutines(bpy.types.Operator):
    bl_idname = "blade.validate_routines"
    bl_label = "✓ Valider toutes les routines"

    def execute(self, context):
        if os.path.exists(SUGGESTED_PATH):
            shutil.copyfile(SUGGESTED_PATH, VALIDATED_PATH)
            os.remove(SUGGESTED_PATH)
            self.report({'INFO'}, "Routines validées avec succès.")
            log.info(" Routines déplacées vers validated.yaml")
        else:
            self.report({'WARNING'}, "Aucune routine à valider.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BLADE_PT_RoutinesPanel)
    bpy.utils.register_class(BLADE_OT_ValidateRoutines)


def unregister():
    bpy.utils.unregister_class(BLADE_PT_RoutinesPanel)
    bpy.utils.unregister_class(BLADE_OT_ValidateRoutines)
