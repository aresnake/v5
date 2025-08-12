# check_imports.py – Détecte tous les fichiers cassés dans Blade

import os
import importlib.util
import traceback

ROOT = os.path.dirname(__file__)
MODULES = []

for root, _, files in os.walk(ROOT):
    for f in files:
        if f.endswith(".py") and f not in ["__init__.py", "check_imports.py", "lint_and_fix.py"]:
            rel_path = os.path.relpath(os.path.join(root, f), ROOT)
            module_name = rel_path.replace("\\", ".").replace("/", ".").replace(".py", "")
            MODULES.append((module_name, os.path.join(root, f)))

print("🔍 Vérification des modules Python Blade v5.1...\n")

for name, path in MODULES:
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {name}")
    except Exception as e:
        print(f"❌ {name} → {e.__class__.__name__}: {e}")
        traceback.print_exc()

print("\n✔️ Vérification terminée.")
