$ErrorActionPreference = 'Stop'

$envDir = 'venv'
if (-not (Test-Path $envDir)) {
    python -m venv $envDir
}

& "$envDir/Scripts/Activate.ps1"

pip install --upgrade pip
pip install .
if (Test-Path 'requirements.txt') {
    pip install -r requirements.txt
}

if (Test-Path '.env.example' -and -not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
}

Write-Host 'Installation complete. Activate with venv\Scripts\activate'

