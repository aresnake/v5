import bpy
import traceback
from ares.core.logger import get_logger

log = get_logger("NonOpsExecutor")

def execute_non_ops_operator(operator_path: str, params: dict) -> bool:
    """
    Excute un oprateur non-`bpy.ops` (accs direct  bpy.context ou bpy.data)
    Exemple : operator_path = "object.active_material.diffuse_color.__setitem__"
    """
    try:
        log.info(f"?? Tentative d'excution directe : {operator_path} avec {params}")

        # Sparation du chemin + mthode spciale ventuelle
        if ".__setitem__" in operator_path:
            base_path = operator_path.replace(".__setitem__", "")
            target = eval(f"bpy.context.{base_path}")
            index = params.get("index", 0)
            value = params.get("value", 1.0)
            target[index] = value
            log.info(f"? __setitem__ appliqu avec succs : {base_path}[{index}] = {value}")
            return True

        # Excution d'une fonction directe
        func = eval(f"bpy.context.{operator_path}")
        if callable(func):
            func(**params)
        else:
            log.warning(f"?? L'oprateur {operator_path} n'est pas appelable")
            return False

        log.info(f"? Oprateur non-ops excut avec succs : {operator_path}")
        return True

    except Exception as e:
        log.error(f"? Erreur non-ops sur {operator_path} : {e}")
        log.debug(traceback.format_exc())
        return False
