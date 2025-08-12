# -*- coding: utf-8 -*-
# ares/tools/render_background.py

from __future__ import annotations

import os
import sys
import tempfile
import datetime
import subprocess
import textwrap
from typing import Tuple, Optional

import bpy
from ares.core.logger import get_logger

log = get_logger("RenderBackground")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _detect_blender_binary() -> str:
    # Utilise le binaire courant (plus robuste que hardcoder un chemin)
    bin_path = getattr(bpy.app, "binary_path", None)
    if not bin_path:
        raise RuntimeError("Blender binaire introuvable (bpy.app.binary_path).")
    return bin_path


def _compute_output_path(blend_path: str, output_dir: str) -> Tuple[str, str]:
    base_dir = os.path.dirname(blend_path)
    abs_output_dir = os.path.abspath(os.path.join(base_dir, output_dir))
    _ensure_dir(abs_output_dir)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    mp4_name = f"video_{now}.mp4"
    mp4_path = os.path.join(abs_output_dir, mp4_name)
    return abs_output_dir, mp4_path


def _make_temp_script(mp4_path: str, res_x: int, res_y: int, fps: int) -> str:
    """
    Crée un petit script temporaire qui s'exécutera dans le Blender lancé en background.
    Note: on re-applique les réglages essentiels côté background.
    """
    script_code = textwrap.dedent(f"""
        import bpy

        scn = bpy.context.scene

        # Sortie MP4 (FFmpeg)
        scn.render.image_settings.file_format = 'FFMPEG'
        scn.render.ffmpeg.format = 'MPEG4'          # conteneur MP4
        scn.render.ffmpeg.codec = 'H264'            # vidéo H.264
        scn.render.ffmpeg.audio_codec = 'AAC'       # audio AAC (si piste présente, VSE ou autre)

        scn.render.resolution_x = {int(res_x)}
        scn.render.resolution_y = {int(res_y)}
        scn.render.fps = {int(fps)}

        # Chemin de sortie (fichier mp4)
        scn.render.filepath = r"{mp4_path}"

        # Rendu animation (frame_start..frame_end)
        bpy.ops.render.render(animation=True)
    """).strip()

    # Emplacement du script temp : dans le dossier temp système (évite permissions)
    tmp_dir = tempfile.gettempdir()
    script_path = os.path.join(tmp_dir, "_blade_render_to_mp4.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_code)

    return script_path


def run_background_render(
    output_dir: str = "renders_video",
    resolution: Tuple[int, int] = (1920, 1080),
    fps: int = 24,
    open_console: bool = True,
    quit_current_blender: bool = True,
) -> Optional[subprocess.Popen]:
    """
    Lance un rendu MP4 en background dans une **nouvelle fenêtre console** (Windows),
    et (optionnellement) ferme le Blender courant.

    Args:
        output_dir: dossier relatif au .blend pour déposer la vidéo
        resolution: (width, height)
        fps: images par seconde
        open_console: ouvre une console dédiée (Windows) pour suivre l'avancement
        quit_current_blender: ferme le Blender courant après lancement

    Returns:
        subprocess.Popen si lancé, sinon None.
    """
    blend_path = bpy.data.filepath
    if not blend_path:
        log.error("❌ Aucun fichier .blend ouvert. Sauvegarde le .blend avant de lancer un rendu background.")
        return None

    try:
        blender_exe = _detect_blender_binary()
    except Exception as e:
        log.error(f"❌ Binaire Blender introuvable: {e}")
        return None

    out_dir, mp4_path = _compute_output_path(blend_path, output_dir)
    res_x, res_y = resolution

    # Applique rapidement les réglages côté session courante (facultatif),
    # puis sauvegarde le .blend pour que le background parte sur un état propre.
    try:
        scn = bpy.context.scene
        scn.render.image_settings.file_format = 'FFMPEG'
        scn.render.ffmpeg.format = 'MPEG4'
        scn.render.ffmpeg.codec = 'H264'
        scn.render.ffmpeg.audio_codec = 'AAC'
        scn.render.resolution_x = int(res_x)
        scn.render.resolution_y = int(res_y)
        scn.render.fps = int(fps)
        scn.render.filepath = mp4_path

        bpy.ops.wm.save_mainfile()
    except Exception as e:
        log.warning(f"⚠️ Impossible d'appliquer/ sauver les réglages avant lancement: {e}")

    # Script qui sera exécuté dans le Blender background
    script_path = _make_temp_script(mp4_path, res_x, res_y, fps)

    # Construction de la commande
    cmd = [
        blender_exe,
        "--background",
        blend_path,
        "--python",
        script_path,
    ]

    log.info(f"🎬 Lancement rendu background → {mp4_path}")
    log.info(f"🧾 Console dédiée: {'ON' if open_console and os.name == 'nt' else 'OFF'}")
    log.debug(f"Cmd: {cmd}")

    # Lancer avec une nouvelle fenêtre console (Windows)
    creationflags = 0
    if open_console and os.name == "nt":
        # Crée une nouvelle console pour suivre le rendu
        creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0x00000010)

    try:
        proc = subprocess.Popen(
            cmd,
            shell=False,                 # important pour gérer les espaces correctement
            creationflags=creationflags, # nouvelle console Windows
        )
        log.info(f"🚀 Rendu lancé (PID={proc.pid}). Sortie: {mp4_path}")
    except Exception as e:
        log.error(f"💥 Échec lancement rendu background: {e}")
        return None

    if quit_current_blender:
        # Ferme l'instance courante pour libérer les ressources
        try:
            bpy.ops.wm.quit_blender()
        except Exception:
            pass

    return proc
