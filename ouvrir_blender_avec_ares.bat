@echo off
:: ============================================================================
:: 🧠 Script : ouvrir_blender_avec_ares.bat
:: 📌 Objectif : créer le lien symbolique "ares" vers Blade v5 dans les addons
:: 📦 Lancer Blender 4.5 avec l’addon Blade activé via lien symbolique
:: ============================================================================

:: 🛡️ Vérifier les droits administrateur
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% NEQ 0 (
    echo 🔐 Ce script nécessite les droits administrateur. Relance en admin...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: ================================
:: ⚙️ CONFIGURATION
:: ================================
set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
set "BLADE_DIR=D:\blender\ares\ares-addon\blade\blade-v5"
set "BLENDER_ADDONS=%APPDATA%\Blender Foundation\Blender\4.5\scripts\addons"
set "LINK_NAME=ares"
set "LINK_PATH=%BLENDER_ADDONS%\%LINK_NAME%"
set "SOURCE_PATH=%BLADE_DIR%\ares"

:: ================================
:: 📁 CRÉATION DOSSIER ADDONS SI MANQUANT
:: ================================
if not exist "%BLENDER_ADDONS%" (
    echo 📂 Création du dossier addons Blender...
    mkdir "%BLENDER_ADDONS%"
)

:: ================================
:: 🧹 SUPPRESSION ANCIEN LIEN
:: ================================
if exist "%LINK_PATH%" (
    echo 🔁 Suppression de l’ancien lien symbolique : %LINK_PATH%
    rmdir "%LINK_PATH%"
) else (
    echo ℹ️ Aucun lien existant à supprimer.
)

:: ================================
:: 🔗 CRÉATION DU LIEN SYMBOLIQUE
:: ================================
echo 🔗 Création du lien : %LINK_PATH% → %SOURCE_PATH%
mklink /D "%LINK_PATH%" "%SOURCE_PATH%"
if errorlevel 1 (
    echo ❌ Échec de création du lien symbolique. Vérifie les chemins.
    pause
    exit /b 1
)

:: ================================
:: 🚀 LANCEMENT DE BLENDER
:: ================================
echo ✅ Lien créé avec succès !
echo 🚀 Lancement de Blender 4.5...
start "" "%BLENDER_EXE%"
exit /b 0
