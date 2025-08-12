"""
Test OperatorClassifier – Vrifie la dtection des types d'oprateurs
"""

from ares.tools.operator_classifier import classify_operator

def test_ops_classification():
    assert classify_operator("bpy.ops.mesh.primitive_cube_add") == "bpy.ops"

def test_context_classification():
    assert classify_operator("bpy.context.object.location") == "bpy.context"

def test_data_classification():
    assert classify_operator("bpy.data.objects['Cube'].location") == "bpy.data"

def test_unknown_classification():
    assert classify_operator("some.other.path") == "unknown"
