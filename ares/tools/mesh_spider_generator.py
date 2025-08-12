# -*- coding: utf-8 -*-
# ares/tools/mesh_spider_generator.py

import bpy
import bmesh
from mathutils import Vector
from math import radians
from typing import List, Optional

# Logger (tolérant à l'arborescence)
try:
    from ares.core.logger import get_logger
except Exception:
    try:
        from ares.core.logger import get_logger
    except Exception:
        def get_logger(_): 
            class _L: 
                def info(self,*a,**k): pass
                def warning(self,*a,**k): pass
                def error(self,*a,**k): pass
                def exception(self,*a,**k): pass
            return _L()

log = get_logger("MeshSpiderGenerator")


def _ensure_object_mode():
    try:
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        pass


def _shade_smooth(objs: List[bpy.types.Object]):
    for ob in objs:
        if ob.type == 'MESH':
            try:
                ob.data.use_auto_smooth = True
                bpy.context.view_layer.objects.active = ob
                bpy.ops.object.shade_smooth()
            except Exception:
                pass


def _new_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def _link_to_collection(ob: bpy.types.Object, col: bpy.types.Collection):
    # Unlink from all, then link to target collection
    try:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
    except Exception:
        pass
    col.objects.link(ob)


def _make_uv_sphere(name: str, radius: float) -> bpy.types.Object:
    _ensure_object_mode()
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radius)
    ob = bpy.context.active_object
    ob.name = name
    return ob


def _make_curve_leg(name: str, points: List[Vector], bevel: float, resolution: int = 2) -> bpy.types.Object:
    # Create a poly Bezier curve with given points, bevel depth → then convert to mesh
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new(type='BEZIER')
    spline.bezier_points.add(len(points) - 1)

    for i, p in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = p
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    curve_data.bevel_depth = float(bevel)
    curve_data.bevel_resolution = 1
    curve_data.resolution_u = max(2, resolution)

    ob = bpy.data.objects.new(name, curve_data)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)

    # Convert to mesh
    _ensure_object_mode()
    try:
        bpy.ops.object.convert(target='MESH')
    except Exception as e:
        log.exception(f"Curve->Mesh convert failed: {e}")
    return ob


def _join_objects(objs: List[bpy.types.Object], name: str) -> Optional[bpy.types.Object]:
    if not objs:
        return None
    _ensure_object_mode()
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    try:
        bpy.ops.object.join()
        joined = bpy.context.active_object
        joined.name = name
        return joined
    except Exception:
        return None


def generate_spider_mesh(
    name: str = "Spider",
    body_radius: float = 0.25,
    abdomen_scale: float = 1.5,
    head_scale: float = 0.75,
    leg_length: float = 0.9,
    leg_bevel: float = 0.02,
    leg_vertical_drop: float = 0.25,
    leg_spread: float = 0.55,
    collection_name: Optional[str] = None,
    with_eyes: bool = True,
) -> bpy.types.Object:
    """
    Génère une araignée procédurale simple :
      - Abdomen (sphere) + Cephalothorax (sphere) + (option) 4x2 pattes (courbes -> mesh)
      - Retourne l'objet parent (Empty) 'name' avec tous les enfants.
    """
    _ensure_object_mode()

    col = _new_collection(collection_name or f"{name}_COL")
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'SPHERE'
    bpy.context.scene.collection.objects.link(root)
    _link_to_collection(root, col)

    # Corps : abdomen + tête
    abdomen = _make_uv_sphere("Abdomen", radius=body_radius * abdomen_scale)
    abdomen.location = Vector((0.0, 0.0, body_radius * 1.05))
    abdomen.parent = root
    _link_to_collection(abdomen, col)

    head = _make_uv_sphere("Cephalothorax", radius=body_radius * head_scale)
    head.location = Vector((0.0, body_radius * 0.75, body_radius * 1.05))
    head.parent = root
    _link_to_collection(head, col)

    eyes_objs: List[bpy.types.Object] = []
    if with_eyes:
        eye_r = body_radius * 0.15
        for dx in (-eye_r*0.9, eye_r*0.9):
            eye = _make_uv_sphere("Eye", radius=eye_r)
            eye.location = head.location + Vector((dx, head.scale.y*0 + body_radius*0.2, body_radius*0.05))
            eye.parent = head
            _link_to_collection(eye, col)
            eyes_objs.append(eye)

    # Pattes (4 par côté)
    leg_objs: List[bpy.types.Object] = []
    # positions sur l’axe Y depuis arrière -> avant
    y_offsets = [-0.25, 0.0, 0.25, 0.5]
    for side in (-1.0, 1.0):  # gauche / droite
        for i, yoff in enumerate(y_offsets):
            base = Vector((side * (body_radius * 0.8), yoff, body_radius * 1.05))
            tip  = base + Vector((side * leg_spread, leg_length * 0.65, -leg_vertical_drop))
            mid1 = base + Vector((side * (leg_spread * 0.4), leg_length * 0.25, 0.0))
            mid2 = base + Vector((side * (leg_spread * 0.8), leg_length * 0.50, -leg_vertical_drop * 0.5))

            leg = _make_curve_leg(
                name=f"Leg_{'R' if side>0 else 'L'}_{i+1}",
                points=[base, mid1, mid2, tip],
                bevel=leg_bevel,
                resolution=2,
            )
            leg.parent = root
            _link_to_collection(leg, col)
            leg_objs.append(leg)

    # Option: joindre pattes en un seul mesh (facultatif, on garde séparé pour édition)
    _shade_smooth([abdomen, head] + eyes_objs + leg_objs)

    # Recentrer origine sur la géométrie globale
    for ob in [abdomen, head] + eyes_objs + leg_objs:
        ob.select_set(False)
    root.select_set(True)
    bpy.context.view_layer.objects.active = root

    return root
