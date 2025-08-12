# ares/tools/text2mesh_manager.py

import os
import uuid
from typing import Any, Optional

import bpy
from mathutils import Vector

# Logger tolérant
try:
    from ares.core.logger import get_logger
except Exception:
    try:
        from ares.core.logger import get_logger
    except Exception:

        def get_logger(_):
            class _L:
                def info(self, *a, **k):
                    pass

                def warning(self, *a, **k):
                    pass

                def error(self, *a, **k):
                    pass

                def exception(self, *a, **k):
                    pass

            return _L()


log = get_logger("Text2MeshManager")

# Générateur procédural
try:
    from ares.tools.mesh_spider_generator import generate_spider_mesh
except Exception as e:
    log.warning(f"mesh_spider_generator import failed: {e}")
    generate_spider_mesh = None

SUPPORTED_EXTS = {".glb", ".gltf", ".fbx", ".obj", ".blend"}

DEFAULT_TEST_PATHS = [
    os.getenv("BLADE_OFFLINE_MODEL_PATH") or "",
    os.path.join(os.path.dirname(__file__), "..", "assets", "test", "spider.glb"),
    os.path.join(os.path.dirname(__file__), "..", "assets", "test", "spider.gltf"),
    os.path.join(os.path.dirname(__file__), "..", "assets", "test", "spider.fbx"),
    os.path.join(os.path.dirname(__file__), "..", "assets", "test", "spider.obj"),
]


# ---------- Helpers ----------
def _first_existing(paths: list[str]) -> str | None:
    for p in paths:
        if p and os.path.exists(os.path.abspath(p)):
            return os.path.abspath(p)
    return None


def _ensure_object_mode():
    try:
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        pass


def _ensure_view_layer_update():
    try:
        bpy.context.view_layer.update()
    except Exception:
        pass


def _import_model(path: str) -> list[bpy.types.Object]:
    path = os.path.abspath(path)
    ext = os.path.splitext(path)[1].lower()
    before = set(bpy.data.objects)

    _ensure_object_mode()

    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=True)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == ".blend":
        with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        for ob in data_to.objects:
            if ob is not None:
                bpy.context.scene.collection.objects.link(ob)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    _ensure_view_layer_update()
    after = set(bpy.data.objects)
    new_objs = list(after - before)
    return new_objs


def _select_and_focus(objs: list[bpy.types.Object]):
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    for ob in objs:
        try:
            ob.select_set(True)
        except Exception:
            pass
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


def _origin_to_geometry(objs: list[bpy.types.Object]):
    for ob in objs:
        try:
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        except Exception:
            pass


def _shade_smooth(objs: list[bpy.types.Object]):
    for ob in objs:
        if ob.type == 'MESH':
            try:
                bpy.context.view_layer.objects.active = ob
                bpy.ops.object.shade_smooth()
            except Exception:
                pass


def _auto_scale(objs: list[bpy.types.Object], target_max_dim: float = 2.0):
    if not objs:
        return
    bbox_min = [1e9, 1e9, 1e9]
    bbox_max = [-1e9, -1e9, -1e9]
    for ob in objs:
        try:
            for v in ob.bound_box:
                world_v = ob.matrix_world @ Vector((v[0], v[1], v[2]))
                for i in range(3):
                    bbox_min[i] = min(bbox_min[i], world_v[i])
                    bbox_max[i] = max(bbox_max[i], world_v[i])
        except Exception:
            pass
    dims = [bbox_max[i] - bbox_min[i] for i in range(3)]
    max_dim = max(dims) if dims else 0.0
    if max_dim <= 0.0:
        return
    scale = target_max_dim / max_dim
    for ob in objs:
        try:
            ob.scale *= scale
        except Exception:
            pass
    _ensure_view_layer_update()


def _postprocess_selected(auto_origin=True, smooth=True, auto_scale_to=None):
    objs = list(bpy.context.selected_objects)
    if not objs:
        return
    if auto_origin:
        _origin_to_geometry(objs)
    if smooth:
        _shade_smooth(objs)
    if isinstance(auto_scale_to, (int, float)) and auto_scale_to > 0:
        _auto_scale(objs, float(auto_scale_to))


# ---------- Job Model ----------
class GenerationStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class GenerationJob:
    def __init__(self, provider: str, prompt: str, params: dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.provider = provider
        self.prompt = prompt
        self.params = params or {}
        self.status = GenerationStatus.PENDING
        self.message = ""
        self.asset_path: str | None = None


# ---------- Manager ----------
class Text2MeshManager:
    """
    start(provider, prompt, **params) -> job_id
    providers:
      - "offline_stub": import d’un modèle local (GLB/FBX/OBJ/BLEND)
                        si vide ou échec → fallback vers "procedural_spider"
      - "procedural_spider": génère une araignée procédurale (sans asset)
    """

    def __init__(self):
        self.jobs: dict[str, GenerationJob] = {}

    def _success(self, job: GenerationJob, msg: str):
        job.status = GenerationStatus.DONE
        job.message = msg
        log.info(msg)

    def _fail(self, job: GenerationJob, msg: str, exc: Exception = None):
        job.status = GenerationStatus.FAILED
        job.message = msg
        if exc:
            log.exception(msg)
        else:
            log.error(msg)

    def _import_and_validate(self, asset_path: str) -> list[bpy.types.Object]:
        new_objs = _import_model(asset_path)
        # Filtrer les meshes réellement créés et non vides
        mesh_objs = [
            o
            for o in new_objs
            if o.type == 'MESH' and getattr(o.data, "vertices", None) and len(o.data.vertices) > 0
        ]
        return mesh_objs

    def start(self, provider: str, prompt: str, **params) -> str:
        job = GenerationJob(provider=provider, prompt=prompt, params=params or {})
        self.jobs[job.id] = job

        try:
            job.status = GenerationStatus.RUNNING
            provider = (provider or "").lower()
            auto_origin = bool(params.get("auto_origin", True))
            smooth = bool(params.get("smooth", True))
            auto_scale_to = params.get("auto_scale_to", None)

            if provider in ("offline_stub", "offline", "local"):
                local = params.get("asset_path") or _first_existing(DEFAULT_TEST_PATHS)
                if not local:
                    self._fail(
                        job,
                        "Aucun fichier local trouvé (définis BLADE_OFFLINE_MODEL_PATH ou place un asset dans ares/assets/test/).",
                    )
                    return job.id

                mesh_objs = self._import_and_validate(local)

                if not mesh_objs:
                    log.warning(
                        f"Import OK mais aucun mesh valide trouvé dans {os.path.basename(local)} → fallback procedural_spider."
                    )
                    if generate_spider_mesh is None:
                        self._fail(job, "Fallback procedural_spider indisponible (import KO).")
                        return job.id
                    root = generate_spider_mesh(
                        name=params.get("name", "Spider"),
                        body_radius=float(params.get("body_radius", 0.25)),
                        abdomen_scale=float(params.get("abdomen_scale", 1.5)),
                        head_scale=float(params.get("head_scale", 0.75)),
                        leg_length=float(params.get("leg_length", 0.9)),
                        leg_bevel=float(params.get("leg_bevel", 0.02)),
                        leg_vertical_drop=float(params.get("leg_vertical_drop", 0.25)),
                        leg_spread=float(params.get("leg_spread", 0.55)),
                        collection_name=params.get("collection_name", None),
                        with_eyes=bool(params.get("with_eyes", True)),
                    )
                    for ob in bpy.context.selected_objects:
                        ob.select_set(False)
                    root.select_set(True)
                    bpy.context.view_layer.objects.active = root
                    _postprocess_selected(
                        auto_origin=auto_origin, smooth=smooth, auto_scale_to=auto_scale_to
                    )
                    job.asset_path = "[procedural_spider_fallback]"
                    self._success(job, "Generated procedural spider (fallback).")
                    return job.id

                # Import réussi avec meshes valides
                for ob in bpy.context.selected_objects:
                    ob.select_set(False)
                for ob in mesh_objs:
                    ob.select_set(True)
                bpy.context.view_layer.objects.active = mesh_objs[0]
                _postprocess_selected(
                    auto_origin=auto_origin, smooth=smooth, auto_scale_to=auto_scale_to
                )
                job.asset_path = local
                self._success(job, f"Imported local asset: {os.path.basename(local)}")
                return job.id

            if provider == "procedural_spider":
                if generate_spider_mesh is None:
                    self._fail(job, "Provider 'procedural_spider' indisponible (import KO).")
                    return job.id
                root = generate_spider_mesh(
                    name=params.get("name", "Spider"),
                    body_radius=float(params.get("body_radius", 0.25)),
                    abdomen_scale=float(params.get("abdomen_scale", 1.5)),
                    head_scale=float(params.get("head_scale", 0.75)),
                    leg_length=float(params.get("leg_length", 0.9)),
                    leg_bevel=float(params.get("leg_bevel", 0.02)),
                    leg_vertical_drop=float(params.get("leg_vertical_drop", 0.25)),
                    leg_spread=float(params.get("leg_spread", 0.55)),
                    collection_name=params.get("collection_name", None),
                    with_eyes=bool(params.get("with_eyes", True)),
                )
                for ob in bpy.context.selected_objects:
                    ob.select_set(False)
                root.select_set(True)
                bpy.context.view_layer.objects.active = root
                _postprocess_selected(
                    auto_origin=auto_origin, smooth=smooth, auto_scale_to=auto_scale_to
                )
                job.asset_path = "[procedural_spider]"
                self._success(job, "Generated procedural spider.")
                return job.id

            self._fail(
                job,
                f"Provider '{provider}' non implémenté (utilise 'offline_stub' ou 'procedural_spider').",
            )
            return job.id

        except Exception as e:
            self._fail(job, f"[Text2Mesh] Generation failed: {e}", exc=e)
            return job.id

    def get(self, job_id: str) -> dict[str, Any] | None:
        j = self.jobs.get(job_id)
        if not j:
            return None
        return {
            "id": j.id,
            "provider": j.provider,
            "prompt": j.prompt,
            "status": j.status,
            "message": j.message,
            "asset_path": j.asset_path,
        }


# ---------- Singleton ----------
_manager_singleton: Optional['Text2MeshManager'] = None


def get_manager() -> 'Text2MeshManager':
    global _manager_singleton
    if _manager_singleton is None:
        _manager_singleton = Text2MeshManager()
    return _manager_singleton
