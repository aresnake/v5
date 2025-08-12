# ares/tools/operator_classifier.py


import bpy

# --- utils --------------------------------------------------------------------


def _sanitize(op: str | None) -> str | None:
    if op is None:
        return None
    op = str(op).strip()

    # Normalize known prefixes
    if op.startswith("bpy.ops."):
        # "bpy.ops.mesh.primitive_cube_add" -> "mesh.primitive_cube_add"
        return op[len("bpy.ops.") :]
    if op.startswith("bpy.context."):
        # "bpy.context.object.location" -> "context.object.location"
        return "context." + op[len("bpy.context.") :]
    if op.startswith("bpy.data."):
        return "data." + op[len("bpy.data.") :]
    return op


def _looks_like_bpy_ops(op: str) -> bool:
    """
    Ops heuristic: first segment must be a valid attribute on bpy.ops
    and there must be at least two segments ("mesh.primitive_cube_add").
    """
    parts = op.split(".")
    if len(parts) < 2:
        return False
    first = parts[0]
    return hasattr(bpy.ops, first)


def _looks_like_context_path(op: str) -> bool:
    """
    context/data paths:
      - "context.object.active_material.diffuse_color"
      - "data.objects['Cube'].location"
    """
    return op.startswith("context.") or op.startswith("data.")


# --- public -------------------------------------------------------------------


def classify_operator(op: str | None) -> str:
    """
    Returns: "ops" | "context" | "unknown"
    Precedence: context/data > ops
    """
    op = _sanitize(op)
    if not op:
        return "unknown"

    # IMPORTANT: give priority to context/data
    if _looks_like_context_path(op):
        return "context"

    if _looks_like_bpy_ops(op):
        return "ops"

    return "unknown"
