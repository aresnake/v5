# ares/tools/intent_resolver.py
# -*- coding: utf-8 -*-

import bpy
import traceback
from typing import Any, Tuple, Optional, Sequence

from ares.core.logger import get_logger
from ares.tools.operator_classifier import classify_operator

log = get_logger("IntentResolver")


# ---------------------------
# Helpers: context preparation
# ---------------------------

def _find_any_editable_object() -> Optional[bpy.types.Object]:
    # Priorité : actif → sélection → dernier mesh de la scène
    obj = bpy.context.view_layer.objects.active
    if obj and not obj.hide_get():
        return obj
    selected = [o for o in bpy.context.selected_objects if not o.hide_get()]
    if selected:
        return selected[-1]
    # fallback: dernier mesh visible
    for o in reversed(list(bpy.context.scene.objects)):
        if o.type in {"MESH", "CURVE", "SURFACE", "META", "GPENCIL"} and not o.hide_get():
            return o
    return None


def ensure_active_object() -> Optional[bpy.types.Object]:
    obj = _find_any_editable_object()
    if obj is None:
        # Créer un cube si rien n'est sélectionnable
        try:
            bpy.ops.object.select_all(action='DESELECT')
        except Exception:
            pass
        try:
            bpy.ops.mesh.primitive_cube_add(size=1.0)
            obj = bpy.context.object
        except Exception:
            log.warning("⚠️ Aucun objet éditable trouvé et création échouée.")
            return None

    # Activer et sélectionner
    try:
        bpy.ops.object.select_all(action='DESELECT')
    except Exception:
        pass
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    return obj


def ensure_active_material(obj: Optional[bpy.types.Object] = None) -> Optional[bpy.types.Material]:
    if obj is None:
        obj = ensure_active_object()
        if obj is None:
            return None

    mat = getattr(obj, "active_material", None)
    if mat is None:
        # Créer un slot + un matériau et l’assigner
        mat = bpy.data.materials.get("Blade_AutoMaterial") or bpy.data.materials.new(name="Blade_AutoMaterial")
        if obj.data and hasattr(obj.data, "materials"):
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.active_material = mat
        else:
            log.warning("⚠️ L’objet actif ne supporte pas les slots matériaux.")
    return obj.active_material


# ---------------------------
# Node helpers (Principled)
# ---------------------------

def _normalize_color(value: Any) -> Any:
    """ Si RGB donné, compléter en RGBA. """
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if len(value) == 3:
            return list(value) + [1.0]
    return value


def _find_material_output(nt: bpy.types.NodeTree) -> Optional[bpy.types.Node]:
    for n in nt.nodes:
        if n.bl_idname == "ShaderNodeOutputMaterial":
            return n
    return None


def _find_principled(nt: bpy.types.NodeTree) -> Optional[bpy.types.Node]:
    for n in nt.nodes:
        if n.bl_idname == "ShaderNodeBsdfPrincipled":
            return n
    return None


def _ensure_principled_pipeline(mat: bpy.types.Material) -> Optional[bpy.types.Node]:
    """Crée un Principled + branche à l'Output si nécessaire, retourne le Principled."""
    if not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    if nt is None:
        log.warning("⚠️ Matériau sans node_tree, impossible de configurer les nodes.")
        return None

    principled = _find_principled(nt)
    if not principled:
        principled = nt.nodes.new("ShaderNodeBsdfPrincipled")
        principled.location = (-200, 200)

    out = _find_material_output(nt)
    if not out:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        out.location = (100, 200)

    # Connecter Principled → Output.Surface si pas déjà connecté
    have_link = False
    for l in nt.links:
        if l.to_node == out and getattr(l.to_socket, "name", "") == "Surface":
            have_link = True
            break
    if not have_link:
        nt.links.new(principled.outputs.get("BSDF"), out.inputs.get("Surface"))

    return principled


def _set_principled_base_color(mat: bpy.types.Material, rgba: Sequence[float]) -> bool:
    """Assigne Base Color (nodes) avec fallback création nodes si nécessaire."""
    try:
        p = _ensure_principled_pipeline(mat)
        if not p:
            return False
        socket = p.inputs.get("Base Color")
        if not socket:
            log.warning("⚠️ Principled sans socket 'Base Color'.")
            return False
        # default_value attend 4 floats
        val = list(_normalize_color(rgba))
        if len(val) < 4:
            val = (val + [1.0, 1.0, 1.0, 1.0])[:4]
        socket.default_value = val[:4]
        log.info(f"🎨 Base Color nodes = {val[:4]}")
        return True
    except Exception as e:
        log.error(f"❌ Échec set Base Color nodes: {e}")
        traceback.print_exc()
        return False


# ---------------------------------------
# Helpers: attribute path parse & set/get
# ---------------------------------------

def _split_attr_and_index(token: str) -> Tuple[str, Optional[int]]:
    """
    Ex.: 'diffuse_color[0]' -> ('diffuse_color', 0)
         'location'         -> ('location', None)
    """
    if "[" in token and token.endswith("]"):
        name, idx_str = token[:-1].split("[", 1)
        try:
            return name, int(idx_str)
        except ValueError:
            return token, None
    return token, None


def _resolve_path(root: Any, dotted_path: str) -> Tuple[Any, Optional[str], Optional[int]]:
    """
    Navigue jusqu'au parent de l’attribut final.
    Retourne (parent_obj, final_attr_name, index_opt)
    Ex.: root=bpy.context, path='object.active_material.diffuse_color[0]'
    """
    if not dotted_path:
        return root, None, None

    tokens = dotted_path.split(".")
    current = root

    for i, tok in enumerate(tokens):
        name, idx = _split_attr_and_index(tok)
        is_last = (i == len(tokens) - 1)

        if not hasattr(current, name):
            raise AttributeError(f"Chemin invalide: '{type(current).__name__}.{name}' n'existe pas.")

        if is_last:
            # On s'arrête au parent; on retourne les infos du dernier token
            return current, name, idx

        current = getattr(current, name)

        if idx is not None:
            # Index intermédiaire (séquence)
            try:
                current = current[idx]
            except Exception as e:
                raise AttributeError(f"Index intermédiaire invalide [{idx}] sur '{name}': {e}") from e

    # Fallback (ne devrait pas arriver)
    return current, None, None


def _assign_value_on_attr(parent: Any, attr: str, idx: Optional[int], value: Any) -> None:
    target = getattr(parent, attr)

    # Si séquence indexable
    if idx is not None:
        try:
            target[idx] = value
            return
        except TypeError:
            raise TypeError(f"Propriété '{attr}' n'accepte pas l'assignation indexée.")
        except Exception as e:
            raise e

    # Assignation directe
    try:
        setattr(parent, attr, value)
    except Exception as e:
        # Certaines propriétés (ex: Color/Vector) exigent une séquence de taille fixe
        if isinstance(value, (int, float)) and hasattr(target, "__len__") and len(target) > 1:
            raise TypeError(
                f"Propriété '{attr}' attend une séquence de longueur {len(target)}, reçu un scalaire."
            ) from e
        raise e


# --------------------------------
# Ops execution with smart fallback
# --------------------------------

def _exec_bpy_ops(operator: str, params: dict) -> bool:
    parts = operator.split(".")
    if len(parts) != 2:
        log.error(f"❌ Format invalide pour opérateur bpy.ops: '{operator}'")
        return False

    category, command = parts
    op_module = getattr(bpy.ops, category, None)
    if not op_module:
        log.error(f"❌ Catégorie inconnue: bpy.ops.{category}")
        return False

    op_func = getattr(op_module, command, None)
    if not op_func or not callable(op_func):
        log.error(f"❌ Commande inconnue: bpy.ops.{category}.{command}")
        return False

    # 1er essai: poll direct
    if hasattr(op_func, "poll") and not op_func.poll():
        log.info(f"🧪 poll()=False pour {operator}, tentative de préparation du contexte…")
        obj = ensure_active_object()
        if obj is None:
            log.warning(f"⚠️ Impossible de préparer un objet actif pour {operator}.")
            return False
        if category == "object" and command in {"modifier_add", "material_slot_add"}:
            ensure_active_material(obj)

        if hasattr(op_func, "poll") and not op_func.poll():
            log.warning(f"⚠️ Contexte toujours invalide pour {operator} après préparation.")
            return False

    # Exécution
    try:
        result = op_func(**(params or {}))
        log.info(f"✅ bpy.ops.{category}.{command} exécuté. Résultat: {result}")
        return True
    except Exception as e:
        log.error(f"❌ Erreur d’exécution bpy.ops.{category}.{command}: {e}")
        traceback.print_exc()
        return False


# ----------------------------------------
# Context execution (direct bpy.context/data)
# ----------------------------------------

def _strip_root_prefix(op: str):
    """
    Retourne (root, path_sans_prefix):
      - 'context.xxx'      -> (bpy.context, 'xxx')
      - 'bpy.context.xxx'  -> (bpy.context, 'xxx')
      - 'data.xxx'         -> (bpy.data, 'xxx')
      - 'bpy.data.xxx'     -> (bpy.data, 'xxx')
      - sinon              -> (bpy.context, op)  # compat
    """
    if op.startswith("bpy.context."):
        return bpy.context, op[len("bpy.context."):]
    if op.startswith("context."):
        return bpy.context, op[len("context."):]
    if op.startswith("bpy.data."):
        return bpy.data, op[len("bpy.data."):]
    if op.startswith("data."):
        return bpy.data, op[len("data."):]
    return bpy.context, op  # tolérance: chemin relatif à context


def _exec_bpy_context(operator: str, params: dict) -> bool:
    """
    Exécution d’un chemin du type:
      - 'context.object.active_material.diffuse_color'  (ou 'object.active_material.diffuse_color')
      - 'data.objects["Cube"].location[0]'
    Règles de rattrapage:
      - Si object actif manquant → sélection/création automatique.
      - Si active_material manquant → création + assignation.
      - Si mat.use_nodes → tente Principled 'Base Color' avant diffuse_color.
    """
    # Préparer un contexte viable
    obj = ensure_active_object()

    # Si le chemin nécessite un matériau actif, on le crée/assigne au besoin
    needs_material = (".active_material" in operator) or ("material" in operator and "diffuse_color" in operator)
    if needs_material:
        mat = ensure_active_material(obj)
    else:
        mat = getattr(bpy.context.object, "active_material", None)

    # Récupérer la valeur à écrire
    if "value" not in params:
        log.warning(f"⚠️ Aucun 'value' fourni pour l’opérateur context: {operator}")
        return False

    value = params.get("value")
    normalize = params.get("normalize", None)
    if normalize == "color":
        value = _normalize_color(value)

    # Si demande de couleur et matériau nodal → régler Base Color nodes en priorité
    if mat and mat.use_nodes and "diffuse_color" in operator:
        if _set_principled_base_color(mat, value):
            return True
        # si nodes KO, on tombera sur l'affectation property ci-dessous

    # Support des préfixes 'context.' / 'bpy.context.' / 'data.' / 'bpy.data.'
    root, path = _strip_root_prefix(operator)

    # Résoudre le chemin
    try:
        parent, attr, idx = _resolve_path(root, path)
        if attr is None:
            log.error(f"❌ Chemin context invalide: '{operator}' (attribut final introuvable)")
            return False

        _assign_value_on_attr(parent, attr, idx, value)
        log.info(f"✅ Contexte '{operator}' affecté avec value={value} (idx={idx})")
        return True

    except Exception as e:
        log.error(f"❌ Erreur d’affectation context '{operator}': {e}")
        traceback.print_exc()
        return False


# ---------------------------
# Public API
# ---------------------------

def resolve_and_execute(intent: dict) -> bool:
    """
    Schéma d’intent attendu (exemples):
      { "name": "ajouter_cube", "operator": "mesh.primitive_cube_add", "params": {"size": 2.0} }
      {
        "name": "changer_couleur_objet",
        "operator": "context.object.active_material.diffuse_color",
        "params": {"value": [1.0, 0.2, 0.2], "normalize": "color"}
      }
      {
        "name": "set_x_location",
        "operator": "object.location[0]",
        "params": {"value": 1.25}
      }
    """
    name = intent.get("name", "intent_sans_nom")
    operator = intent.get("operator")
    params = intent.get("params", {}) or {}

    if not operator:
        log.error(f"❌ Intent '{name}': opérateur manquant.")
        return False

    # Priorité: si le chemin ressemble à du context/data, on force "context"
    if operator.startswith(("context.", "bpy.context.", "data.", "bpy.data.")):
        operator_type = "context"
    else:
        operator_type = classify_operator(operator)

    log.info(f"🔎 Résolution de '{name}' → operator='{operator}' (type: {operator_type})")

    try:
        if operator_type == "ops":
            return _exec_bpy_ops(operator, params)
        elif operator_type == "context":
            return _exec_bpy_context(operator, params)
        else:
            # Tolérance: retenter en "context" si le format s'y prête
            if operator.startswith(("context.", "bpy.context.", "data.", "bpy.data.")):
                return _exec_bpy_context(operator, params)
            log.warning(f"⚠️ Type d’opérateur non supporté pour '{name}': {operator_type}")
            return False
    except Exception as e:
        log.error(f"❌ Erreur pendant l'exécution de '{name}' ({operator}): {e}")
        traceback.print_exc()
        return False
