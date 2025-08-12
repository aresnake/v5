# run_blender_tests.ps1

# Lancer les tests vocaux Blade v5 dans Blender en mode background

$blenderPath = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
$projectDir = "D:\blender\ares\ares-addon\blade\blade-v5"
$testScript = "$projectDir\tests\test_voice_config_all_intents.py"

Write-Host "🚀 Lancement des tests Blade v5 dans Blender..."

& "$blenderPath" --background --factory-startup --python-expr "import sys; sys.path.insert(0, '$projectDir'); exec(compile(open('$testScript', encoding='utf-8').read(), '$testScript', 'exec'))"

Write-Host "✅ Tests terminés. Vérifie les logs et summary/"
