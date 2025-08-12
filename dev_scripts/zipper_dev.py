"""
ZipperDev – Archive l'addon Blade v5 pour Blender
Gnre un fichier ZIP prt  tre install dans Blender.
"""

import os
import zipfile

ADDON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ares"))
OUTPUT_ZIP = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "builds-dev", "blade-addon.zip")
)


def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.dirname(folder_path))
                zipf.write(abs_path, rel_path)

    print(f"? ZIP gnr : {output_path}")


if __name__ == "__main__":
    zip_folder(ADDON_DIR, OUTPUT_ZIP)
