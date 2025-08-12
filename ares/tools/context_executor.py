import bpy

from ares.core.logger import get_logger

log = get_logger("ContextExecutor")


def execute_direct_path(operator: str, params: dict):
    """
    ExÃ©cute un accÃ¨s direct Ã  une propriÃ©tÃ© de Blender (ex: object.active_material.diffuse_color.__setitem__)
    avec fallback automatique.
    """
    try:
        # ðŸ” Gestion des setitem
        if ".__setitem__" in operator:
            path = operator.replace(".__setitem__", "")
            ensure_context_for_path(path)

            attr = resolve_bpy_path(path)
            index = params.get("index", 0)
            value = params.get("value", 0.0)

            log.info(f"ðŸ”§ Setitem : {path}[{index}] = {value}")
            attr[index] = value
            return True

        log.warning(f"âš ï¸ OpÃ©rateur direct non pris en charge : {operator}")
        return False

    except Exception as e:
        log.error(f"âŒ Erreur dans execute_direct_path : {e}")
        return False


def resolve_bpy_path(path: str):
    """
    RÃ©sout une chaÃ®ne comme "object.active_material.diffuse_color" en objet rÃ©el Blender.
    """
    current = bpy.context
    for part in path.split("."):
        current = getattr(current, part)
    return current


def ensure_context_for_path(path: str):
    """
    CrÃ©e automatiquement les Ã©lÃ©ments manquants pour que le path soit valide.
    Exemples :
    - active_object
    - active_material
    - active_material.diffuse_color
    """
    if "object.active_material" in path:
        ensure_object_selected()
        ensure_material_on_object()


def ensure_object_selected():
    """
    SÃ©lectionne un objet actif si aucun n'est sÃ©lectionnÃ©.
    """
    if not bpy.context.object:
        objs = bpy.data.objects
        for obj in objs:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                log.info(f"ðŸ” Objet sÃ©lectionnÃ© automatiquement : {obj.name}")
                return


def ensure_material_on_object():
    """
    CrÃ©e un matÃ©riau s'il n'existe pas sur l'objet actif.
    """
    obj = bpy.context.object
    if not obj:
        return

    if not obj.data.materials:
        mat = bpy.data.materials.new(name="Mat_Auto")
        obj.data.materials.append(mat)
        log.info(f"ðŸŽ¨ MatÃ©riau ajoutÃ© automatiquement Ã  {obj.name}")
    elif not obj.active_material:
        obj.active_material = obj.data.materials[0]
        log.info(f"ðŸŽ¨ MatÃ©riau actif dÃ©fini : {obj.active_material.name}")
