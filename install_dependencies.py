# install_dependencies.py

"""
Installe automatiquement les dépendances requises pour Blade v5 si manquantes.
Peut être appelé depuis l'addon ou en ligne de commande.
"""

import subprocess
import sys

REQUIRED_PACKAGES = [
    "pyyaml>=6.0",
    "openai>=1.0.0",
    "speechrecognition",
    "pyaudio",
    "httpx",
    "requests",
    "matplotlib",
    "pytest",
    "flake8",
    "autoflake",
]


def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installé : {package}")
    except Exception as e:
        print(f"❌ Erreur d'installation pour {package} : {e}")


def main():
    print("🔍 Vérification des dépendances Python...")
    for pkg in REQUIRED_PACKAGES:
        install(pkg)


if __name__ == "__main__":
    main()
