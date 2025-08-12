"""
Test ContextPreparer – Vrifie que les fonctions contextuelles s'excutent sans erreur
Note : ncessite Blender lanc avec environnement bpy
"""

import bpy
from ares.tools.context_preparer import (
    ensure_active_object,
    ensure_material_exists,
    ensure_material_slot,
    prepare_context_if_needed
)

def test_prepare_context_minimal():
    # Cre un cube temporaire pour le test
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    assert obj is not None

    ensure_active_object()
    ensure_material_exists(obj)
    ensure_material_slot(obj)

    # Simulation d’intent avec besoin de matriau
    intent = {
        "name": "test_couleur",
        "operator": "bpy.context.object.active_material.diffuse_color"
    }
    prepare_context_if_needed(intent)

    assert obj.active_material is not None
    assert len(obj.material_slots) > 0
