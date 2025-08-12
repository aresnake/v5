# 🔒 make_zip.ps1 – Copie NON destructive

$projectRoot = "D:\blender\ares\ares-addon\blade\blade-v5"
$source = Join-Path $projectRoot "ares"
$zipPath = Join-Path $projectRoot "blade-v5.1.zip"

# Vérif de sécurité
if (-not (Test-Path $source)) {
    Write-Host "❌ Le dossier 'ares/' est introuvable. Vérifie qu’il existe bien dans blade-v5/"
    exit 1
}

# Copie temporaire dans un dossier propre
$temp = Join-Path $projectRoot "temp_zip"
if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
New-Item -Path $temp -ItemType Directory | Out-Null

# Copie de ares/ → temp/ares/
Copy-Item -Path $source -Destination (Join-Path $temp "ares") -Recurse

# Création du zip sans toucher à l’original
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$temp\ares" -DestinationPath $zipPath -Force

# Nettoyage
Remove-Item $temp -Recurse -Force

Write-Host "✅ blade-v5.1.zip généré avec le dossier ares/ (addon intact)."
