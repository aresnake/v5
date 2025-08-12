# 🧪 Lance tous les intents de voice_config.yaml dans Blender (background)
$blenderExe = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
$scriptPath = "D:\blender\ares\ares-addon\blade\blade-v5\tests\run_all_intents_blender.py"

Write-Host "🧠 Lancement des tests vocaux dans Blender..."
& "$blenderExe" --background --factory-startup --python "$scriptPath"
