# ✅ Fichier : ares/__init__.py (corrigé UTF-8)

bl_info = {
    "name": "Blade v5.1",
    "author": "Team Blade",
    "version": (5, 1),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Blade",
    "description": "Assistant vocal et IA adaptative pour Blender",
    "category": "3D View",
}

import importlib

import bpy

from ares.core.logger import get_logger

log = get_logger("Init")

# Modules à recharger dynamiquement (pour dev)
modules = [
    "core.run_pipeline",
    "core.intent_parser",  # ✅ correction : anciennement voice.intent_parser
    "tools.intent_resolver",
    "tools.intent_executor",
    "tools.validate_suggestions",
    "tools.utils_yaml",
    "bots.injector_bot",
    "agents.agent_passif",  # ✅ correction : anciennement bots.passive_agent
    "bots.editor_watcher",
    "voice.voice_engine",
    "voice.voice_config_manager",
    "ui.ui_main",
    "ui.ui_suggestions",
    "ui.ui_codex",
    "ui.ui_routines",
    "ui.ui_spider_generator",  # ✅ ajout UI Spider
]

for m in modules:
    try:
        importlib.reload(importlib.import_module(f"ares.{m}"))
    except Exception as e:
        log.error(f"❌ Erreur au rechargement de {m} : {e}")


# Enregistreurs UI / Bots / etc.
def register():
    from ares.agents.agent_passif import activate_passive_agent
    from ares.bots.editor_watcher import register_handler

    from .ui import (
        ui_codex,
        ui_main,
        ui_routines,
        ui_spider_generator,  # ✅ ajout
        ui_suggestions,
    )

    log.info("🔌 Initialisation de Blade Voice Assistant")
    ui_main.register()
    ui_suggestions.register()
    ui_codex.register()
    ui_routines.register()
    ui_spider_generator.register()  # ✅ ajout

    register_handler()
    activate_passive_agent()  # Passive seulement


def unregister():
    from ares.agents.agent_passif import deactivate_passive_agent
    from ares.bots.editor_watcher import unregister_handler

    from .ui import (
        ui_codex,
        ui_main,
        ui_routines,
        ui_spider_generator,  # ✅ ajout
        ui_suggestions,
    )

    ui_main.unregister()
    ui_suggestions.unregister()
    ui_codex.unregister()
    ui_routines.unregister()
    ui_spider_generator.unregister()  # ✅ ajout

    unregister_handler()
    deactivate_passive_agent()
