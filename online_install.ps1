# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
$ErrorActionPreference = 'Stop'

$envDir = 'venv'
$python = if ($env:PYTHON) { $env:PYTHON } else { 'python3' }
if (-not (Get-Command $python -ErrorAction SilentlyContinue)) {
    $python = 'python'
}

$createdEnv = $false
if (-not $env:VIRTUAL_ENV) {
    if (-not (Test-Path $envDir)) {
        & $python -m venv $envDir
        $createdEnv = $true
    }
    & "$envDir/Scripts/Activate.ps1"
}

pip install --upgrade pip
pip install "git+https://github.com/BP-H/superNova_2177.git"
pip install -r requirements.txt

if (Test-Path '.env.example' -and -not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
}

Write-Host 'Installation complete.'
if ($createdEnv) {
    Write-Host "Activate the environment with '.\\$envDir\\Scripts\\activate'"
}
Write-Host 'Set SECRET_KEY in the environment or the .env file before running the app.'

