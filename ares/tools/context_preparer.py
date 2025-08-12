"""
ContextPreparer â€“ Corrige les erreurs de contexte Blender automatiquement.
UtilisÃ© par intent_resolver.py si un poll() Ã©choue.
"""

import bpy
from ares.core.logger import get_logger

log = get_logger("ContextPreparer")

def ensure_active_object():
    if bpy.context.active_object is None:
        objects = bpy.context.selected_objects or bpy.context.scene.objects
        if objects:
            bpy.context.view_layer.objects.active = objects[0]
            log.info(f"ðŸ”§ Objet actif dÃ©fini automatiquement : {objects[0].name}")
        else:
            log.warning("âŒ Aucun objet disponible pour Ãªtre actif.")

def ensure_material_exists(obj):
    if not obj.data or not hasattr(obj.data, "materials"):
        log.warning("âŒ Lâ€™objet ne supporte pas les matÃ©riaux.")
        return

    if len(obj.data.materials) == 0:
        mat = bpy.data.materials.new(name="AutoMaterial")
        obj.data.materials.append(mat)
        log.info(f"ðŸ§± MatÃ©riau ajoutÃ© automatiquement : {mat.name}")
    else:
        log.debug("ðŸŽ¨ MatÃ©riau dÃ©jÃ  prÃ©sent.")

def ensure_material_slot(obj):
    if not obj.material_slots:
        try:
            bpy.ops.object.material_slot_add()
            log.info("ðŸ§© Slot de matÃ©riau ajoutÃ©.")
        except Exception as e:
            log.error(f"ðŸ’¥ Erreur lors de lâ€™ajout du slot de matÃ©riau : {e}")

def prepare_context_if_needed(intent: dict) -> bool:
    """
    VÃ©rifie et prÃ©pare le contexte Blender si nÃ©cessaire :
    - Objet actif
    - MatÃ©riau
    - Slot de matÃ©riau
    """
    log.info(f"ðŸ› ï¸ PrÃ©paration du contexte pour : {intent.get('name', 'intent inconnu')}")

    ensure_active_object()
    obj = bpy.context.active_object

    if not obj:
        log.warning("âŒ Aucun objet actif aprÃ¨s tentative.")
        return False

    operator = intent.get("operator") or ""
    context_modified = False

    if "material" in operator or "diffuse_color" in operator or "shading" in operator:
        ensure_material_exists(obj)
        ensure_material_slot(obj)
        context_modified = True

    log.info("âœ… Contexte prÃªt.")
    return context_modified
