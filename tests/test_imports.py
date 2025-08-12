# tests/test_imports.py

import importlib
import traceback

MODULES = [
    # Core
    "ares.core.logger",
    "ares.core.intent_parser",
    "ares.core.intent_router",
    "ares.core.intent_executor",
    "ares.core.command_router",
    "ares.core.run_pipeline",
    # Voice
    "ares.voice.voice_engine",
    "ares.voice.voice_config_manager",
    # Bots
    "ares.bots.session_log_enricher_bot",
    "ares.bots.injector_bot",
    # Tools
    "ares.tools.operator_classifier",
    "ares.tools.context_preparer",
    "ares.tools.intent_resolver",
    "ares.tools.non_ops_executor",
    "ares.tools.context_executor",
    # UI
    "ares.ui.ui_main",
]

print("🔍 Démarrage des tests d'import Blade v5...\n")

for module_name in MODULES:
    try:
        importlib.import_module(module_name)
        print(f"✅ Import réussi : {module_name}")
    except Exception:
        print(f"❌ Import échoué : {module_name}")
        traceback.print_exc()

print("\n🎯 Test d'import terminé.")
