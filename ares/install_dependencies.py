import os
import subprocess
import sys

import pkg_resources

from ares.core.logger import get_logger

log = get_logger("DependencyInstaller")

# Fichier requirements.txt
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
REQUIREMENTS_FILE = os.path.join(CONFIG_DIR, "requirements.txt")

# Fichier log pour les erreurs
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
ERROR_LOG_FILE = os.path.join(LOGS_DIR, "dependency_errors.log")

# Packages qui nécessitent confirmation (API, gros modules, ou problématiques)
CONFIRMATION_REQUIRED = {
    "openai",  # Utilisation d'une API payante
    "pyaudio",  # Installation parfois complexe
    "speechrecognition",  # Utilise micro et accès audio
}


def read_requirements():
    """Lit requirements.txt et retourne une liste de packages."""
    if not os.path.exists(REQUIREMENTS_FILE):
        log.error(f"❌ Fichier requirements.txt introuvable : {REQUIREMENTS_FILE}")
        return []
    with open(REQUIREMENTS_FILE, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return lines


def is_installed(pkg_spec):
    """Vérifie si un package est déjà installé avec la bonne version."""
    try:
        pkg_resources.require([pkg_spec])
        return True
    except pkg_resources.DistributionNotFound:
        return False
    except pkg_resources.VersionConflict:
        return False


def install_package(pkg_spec):
    """Installe un package silencieusement et gère les erreurs."""
    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--disable-pip-version-check",
                pkg_spec,
            ]
        )
        log.info(f"✅ {pkg_spec} installé avec succès.")
        return True
    except Exception as e:
        log.error(f"❌ Erreur installation {pkg_spec} : {e}")
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as err_file:
            err_file.write(f"{pkg_spec} | {e}\n")
        return False


def needs_confirmation(pkg_spec):
    """Vérifie si un package est dans la liste à confirmation."""
    pkg_name = pkg_spec.split(">=")[0].split("==")[0].lower()
    return pkg_name in CONFIRMATION_REQUIRED


def install_all():
    """Vérifie et installe les dépendances manquantes/mal versionnées."""
    log.info("🔍 Vérification des dépendances Python...")
    requirements = read_requirements()

    if not requirements:
        log.warning("⚠️ Aucun package trouvé dans requirements.txt")
        return

    for pkg in requirements:
        if not is_installed(pkg):
            if needs_confirmation(pkg):
                log.warning(f"📦 Package nécessitant autorisation : {pkg}")
                user_input = input(f"Installer {pkg} ? (O/N) : ").strip().lower()
                if user_input != "o":
                    log.info(f"⏭ Installation ignorée pour : {pkg}")
                    continue
            install_package(pkg)
        else:
            log.info(f"✔ {pkg} déjà installé et à jour.")


if __name__ == "__main__":
    install_all()
