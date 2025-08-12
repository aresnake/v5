# tasks/package_addon.py

"""
Génère un ZIP de l'addon Blade v5 prêt à être installé dans Blender
Inclut uniquement le dossier ares/ (code principal)
"""

import os
import zipfile

ADDON_DIR = os.path.join(os.path.dirname(__file__), "..", "ares")
OUTPUT_ZIP = os.path.join(os.path.dirname(__file__), "..", "blade_v5_addon.zip")


def zip_addon():
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ADDON_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, os.path.dirname(ADDON_DIR))
                zipf.write(full_path, rel_path)
                print(f"+ {rel_path}")

    print(f"✅ Addon packagé avec succès : {OUTPUT_ZIP}")


if __name__ == '__main__':
    zip_addon()

