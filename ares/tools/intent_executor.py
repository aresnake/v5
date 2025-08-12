# ares/tools/intent_executor.py
# -*- coding: utf-8 -*-

"""
IntentExecutor – exécute un intent unique ou un lot d'intents avec robustesse.

✔️ Pipeline :
    1) Appel primaire : resolve_and_execute(intent)  [tools.intent_resolver]
    2) En cas d'échec → fallback interne :
        - Exécution bpy.ops (si "op" fourni)
        - Accès direct (si "direct" fourni) ex: "context.object.name", "data.objects['Cube'].location[0]"
    3) Auto-fix optionnel du contexte (objet actif, matériau, slot…), puis retry.

Format d'intent attendu (souple) :
{
  "name": "ajouter_cube",
  "op": "mesh.primitive_cube_add",        # optionnel – pour bpy.ops
  "args": [],                              # optionnel
  "kwargs": {"size": 2.0},                 # optionnel
  "direct": {"path": "context.scene.frame_end", "value": 250},   # optionnel
  "requires": ["active_object"],           # optionnel – aide auto_fix
  "ensure": ["active_object", "material"], # optionnel – aide auto_fix
  "meta": {"tags": ["objects", "add"]}     # libre
}

Notes :
- On ne fait AUCUN eval/exec dynamique côté utilisateur.
- Le parsing d’indexation simple [i] est supporté pour le dernier segment.
- Les auto-fix sont minimaux et sûrs (création cube, mat par défaut).
"""

from __future__ import annotations

import time
import traceback
from typing import Iterable, Dict, Any, List, Tuple, Optional

import bpy

from ares.core.logger import get_logger
from ares.tools.intent_resolver import resolve_and_execute

log = get_logger("IntentExecutor")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _short_stack() -> str:
    """Retourne un stacktrace compact pour les logs."""
    return "".join(traceback.format_exc(limit=5))


def _get_bpy_ops_callable(op_path: str):
    """
    Retourne l'appelable bpy.ops.* à partir d'un chemin style "mesh.primitive_cube_add".
    Lève AttributeError si non trouvable.
    """
    node = bpy.ops
    for part in op_path.split("."):
        node = getattr(node, part)
    return node


def _parse_last_index(segment: str) -> Tuple[str, Optional[int]]:
    """
    Détecte une indexation finale de type 'attr[0]'.
    Retourne (base_attr, index_int_or_None).
    """
    if "[" in segment and segment.endswith("]"):
        base, idx = segment.split("[", 1)
        idx = idx[:-1]  # drop ]
        try:
            return base, int(idx)
        except ValueError:
            return segment, None
    return segment, None


def _walk_bpy_path(path: str) -> Tuple[Any, str, Optional[int]]:
    """
    Navigue dans un chemin de type:
      - "context.scene.frame_end"
      - "data.objects['Cube'].location[0]"
      - "context.object.active_material.diffuse_color[1]"

    Retourne (parent_obj, last_attr_name, last_index_or_None) pour un set.
    Supporte une indexation finale [i]. Supporte l'accès dict ['Key'] au milieu.
    """
    # On n'autorise que "bpy.context" et "bpy.data" comme racines
    if not (path.startswith("context.") or path.startswith("data.")):
        raise ValueError("Path must start with 'context.' or 'data.' (without 'bpy.').")
    root_name, rest = path.split(".", 1)

    node = getattr(bpy, root_name)  # bpy.context ou bpy.data

    # Découpage custom qui conserve les segments avec quotes/brackets
    segments: List[str] = []
    cur = ""
    bracket = 0
    quote = None
    for ch in rest:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            cur += ch
            continue
        if ch == "[":
            bracket += 1
            cur += ch
            continue
        if ch == "]":
            bracket -= 1
            cur += ch
            continue
        if ch == "." and bracket == 0:
            segments.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        segments.append(cur)

    # On parcourt jusqu'au dernier parent
    for seg in segments[:-1]:
        # Dict style objects['Cube']
        if "[" in seg and seg.endswith("]"):
            before, key = seg.split("[", 1)
            key = key[:-1]  # drop ]
            if (key.startswith("'") and key.endswith("'")) or (key.startswith('"') and key.endswith('"')):
                key = key[1:-1]
            container = getattr(node, before)
            node = container[key]
        else:
            node = getattr(node, seg)

    last = segments[-1]
    last_attr, last_index = _parse_last_index(last)
    parent = node
    return parent, last_attr, last_index


def _set_bpy_path_value(path: str, value: Any):
    """
    Définit une valeur via un chemin 'context.*' / 'data.*'.
    Gère l’indexation finale type [i].
    """
    parent, last_attr, last_index = _walk_bpy_path(path)
    target = getattr(parent, last_attr)
    if last_index is None:
        # Affectation directe
        setattr(parent, last_attr, value)
    else:
        # Affectation indexée
        target[last_index] = value


# ---------------------------------------------------------------------------
# Auto-fix minimal du contexte
# ---------------------------------------------------------------------------

def _ensure_active_object() -> bpy.types.Object:
    obj = bpy.context.object
    if obj is None:
        # Création d'un cube par défaut, sélection/activation
        try:
            bpy.ops.mesh.primitive_cube_add(size=1.0)
            obj = bpy.context.object
            if obj:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
        except Exception:  # pragma: no cover
            log.error("❌ Échec création d'un objet par défaut.", exc_info=True)
    return bpy.context.object


def _ensure_active_material(obj: bpy.types.Object) -> bpy.types.Material | None:
    if obj is None:
        return None
    if obj.active_material:
        return obj.active_material
    # Crée / assigne un mat par défaut
    try:
        mat = bpy.data.materials.get("Blade_Default") or bpy.data.materials.new("Blade_Default")
        if obj.data and hasattr(obj.data, "materials"):
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat
        obj.active_material = mat
        return mat
    except Exception:  # pragma: no cover
        log.error("❌ Échec ensure material.", exc_info=True)
    return obj.active_material


def _auto_fix_context(intent: Dict[str, Any]):
    """
    Applique des corrections minimales en fonction de intent['requires'] / intent['ensure'].
    """
    requires = intent.get("requires", []) or []
    ensure = intent.get("ensure", []) or []

    if "active_object" in requires or "active_object" in ensure:
        obj = _ensure_active_object()
        if obj is None:
            log.warning("⚠️ Impossible de garantir un objet actif.")

    if "material" in ensure:
        obj = bpy.context.object
        if obj is None:
            obj = _ensure_active_object()
        _ = _ensure_active_material(obj)


# ---------------------------------------------------------------------------
# Fallback executors
# ---------------------------------------------------------------------------

def _try_bpy_ops(intent: Dict[str, Any]) -> Tuple[bool, str]:
    op = intent.get("op")
    if not op:
        return False, "No 'op' provided."
    args = intent.get("args") or []
    kwargs = intent.get("kwargs") or {}
    try:
        fn = _get_bpy_ops_callable(op)
        res = fn(*args, **kwargs)
        # Les opérateurs Blender renvoient set({'FINISHED'}) ou {'CANCELLED'}
        if isinstance(res, set) and "FINISHED" in res:
            return True, "FINISHED"
        # Certains ops renvoient None quand tout va bien
        if res is None:
            return True, "FINISHED(None)"
        # Si retour inattendu mais pas d'exception → considérer ok
        return True, f"FINISHED({res})"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _try_direct_set(intent: Dict[str, Any]) -> Tuple[bool, str]:
    direct = intent.get("direct")
    if not direct or not isinstance(direct, dict):
        return False, "No 'direct' dict provided."
    path = direct.get("path")
    if not path:
        return False, "No 'path' in 'direct'."
    if path.startswith("bpy."):
        # On demande 'context.' ou 'data.' (sans préfixe 'bpy.')
        path = path[len("bpy."):]
    value = direct.get("value")
    try:
        _set_bpy_path_value(path, value)
        return True, "SET"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def execute_intent(
    intent: Dict[str, Any],
    *,
    auto_fix: bool = True,
    retries: int = 1,
    delay_s: float = 0.05,
) -> Dict[str, Any]:
    """
    Exécute un intent unique de manière robuste.

    Retour:
      {
        "name": str,
        "ok": bool,
        "stage": "resolver" | "fallback_ops" | "fallback_direct" | "failed",
        "message": str,
        "error": Optional[str]
      }
    """
    name = intent.get("name") or intent.get("id") or "intent"
    summary: Dict[str, Any] = {"name": name, "ok": False, "stage": None, "message": "", "error": None}

    if not isinstance(intent, dict):
        msg = "❌ Intent must be a dict."
        log.error(msg)
        summary.update(stage="failed", message=msg)
        return summary

    # 1) Essai principal : resolver
    try:
        result = resolve_and_execute(intent)
        if result and (result is True or result.get("ok") is True):
            summary.update(ok=True, stage="resolver", message="resolver:ok")
            return summary
    except Exception:
        log.debug(f"Resolver a levé une exception sur '{name}'.", exc_info=True)

    # 2) Auto-fix + retries
    tries = max(1, int(retries) + 1)  # ex : retries=1 → 2 passages (fix + retry)
    for idx in range(tries):
        if auto_fix:
            try:
                _auto_fix_context(intent)
            except Exception:
                log.debug("Auto-fix context: exception ignorée.", exc_info=True)

        # 2a) Fallback via bpy.ops
        ok, msg = _try_bpy_ops(intent)
        if ok:
            summary.update(ok=True, stage="fallback_ops", message=msg)
            return summary

        # 2b) Fallback accès direct
        ok, msg2 = _try_direct_set(intent)
        if ok:
            summary.update(ok=True, stage="fallback_direct", message=msg2)
            return summary

        # Retarder avant tentative suivante
        if idx < tries - 1:
            time.sleep(max(0.0, float(delay_s)))

    # 3) Échec
    err = f"resolver+fallback failed | ops='{intent.get('op')}' | direct='{(intent.get('direct') or {}).get('path')}'"
    log.error(f"❌ Échec intent '{name}'. {err}\n{_short_stack()}")
    summary.update(stage="failed", message="failed", error=err)
    return summary


def execute_batch(
    intents: Iterable[Dict[str, Any]],
    *,
    auto_fix: bool = True,
    retries: int = 1,
    delay_s: float = 0.05,
    stop_on_error: bool = False,
) -> Dict[str, Any]:
    """
    Exécute un lot d'intents et retourne un résumé.
    """
    details: List[Dict[str, Any]] = []
    ok_count = 0
    failed_count = 0
    names_success: List[str] = []
    names_failed: List[str] = []

    if not isinstance(intents, Iterable):
        raise TypeError("intents must be iterable of dicts")

    for intent in intents:
        try:
            res = execute_intent(intent, auto_fix=auto_fix, retries=retries, delay_s=delay_s)
            details.append(res)
            if res.get("ok"):
                ok_count += 1
                names_success.append(res.get("name") or "intent")
            else:
                failed_count += 1
                names_failed.append(res.get("name") or "intent")
                if stop_on_error:
                    break
        except Exception:
            failed_count += 1
            name = (intent or {}).get("name") if isinstance(intent, dict) else "intent"
            names_failed.append(name or "intent")
            details.append({"name": name, "ok": False, "stage": "failed", "message": "exception", "error": _short_stack()})
            if stop_on_error:
                break

    total = ok_count + failed_count
    summary = {
        "total": total,
        "success": ok_count,
        "failed": failed_count,
        "names_success": names_success,
        "names_failed": names_failed,
        "details": details,
    }

    log.info(f"📊 Résumé batch intents → total={total} | success={ok_count} | failed={failed_count}")
    if failed_count:
        log.warning(f"❗ Intents échoués: {names_failed}")

    return summary
