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
pip install supernova-2177

if (Test-Path '.env.example' -and -not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
}

Write-Host 'Installation complete.'
if ($createdEnv) {
    Write-Host "Activate the environment with '.\\$envDir\\Scripts\\activate'"
}
Write-Host 'Set SECRET_KEY in the environment or the .env file before running the app.'

