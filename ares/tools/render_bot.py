# ðŸ“ ares/tools/render_bot.py

import datetime
import os
import subprocess

import bpy

from ares.core.logger import get_logger

log = get_logger("RenderBot")


def launch_background_render(output_dir="renders_video", resolution=(1920, 1080), fps=24):
    blend_path = bpy.data.filepath
    if not blend_path:
        log.error("âŒ Aucun fichier .blend ouvert.")
        return

    abs_output_dir = os.path.abspath(os.path.join(os.path.dirname(blend_path), output_dir))
    os.makedirs(abs_output_dir, exist_ok=True)

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    mp4_name = f"video_{now}.mp4"
    mp4_path = os.path.join(abs_output_dir, mp4_name)

    scene = bpy.context.scene
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.fps = fps
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.filepath = mp4_path

    bpy.ops.wm.save_mainfile()

    script_path = os.path.join(os.path.dirname(blend_path), "render_to_mp4.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(
            f"""
import bpy
bpy.context.scene.render.filepath = r"{mp4_path}"
bpy.ops.render.render(animation=True)
"""
        )

    blender_exe = "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe"
    cmd = [blender_exe, "--background", blend_path, "--python", script_path]

    log.info(f"ðŸŽ¬ Rendu en cours dans : {mp4_path}")
    subprocess.Popen(cmd, shell=True)
    bpy.ops.wm.quit_blender()
