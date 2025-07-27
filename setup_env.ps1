$ErrorActionPreference = 'Stop'

$envDir = 'venv'

# Determine Python interpreter
$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "Python not found. Please install Python 3.12 or newer."
    exit 1
}

# Ensure Python version is >= 3.12
& $python -c "import sys; exit(0 if sys.version_info >= (3,12) else 1)"
if ($LASTEXITCODE -ne 0) {
    $ver = & $python --version
    Write-Error "Python 3.12 or higher is required. Current version: $ver"
    exit 1
}

# Create virtual environment if missing
if (-not (Test-Path $envDir)) {
    & $python -m venv $envDir
}

& "$envDir/Scripts/Activate.ps1"

pip install --upgrade pip
if (Test-Path 'requirements.txt') {
    pip install -r requirements.txt
}

pip install .

if (Test-Path '.env.example' -and -not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
}

Write-Host "Setup complete. Activate with venv\Scripts\activate"
