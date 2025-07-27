$ErrorActionPreference = 'Stop'

$envDir = 'venv'
if (-not (Test-Path $envDir)) {
    python -m venv $envDir
}

& "$envDir/Scripts/Activate.ps1"

pip install --upgrade pip
if (Test-Path 'requirements.lock') {
    pip install -r requirements.lock
} elseif (Test-Path 'requirements.txt') {
    pip install -r requirements.txt
}

pip install .

if (Test-Path '.env.example' -and -not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
}

Write-Host "Setup complete. Activate with venv\Scripts\activate"
