# Development Setup

This repository targets **Python 3.11** and uses standard tooling for managing dependencies and tests.

## Prerequisites

1. Install Python 3.11.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows use .\venv\Scripts\activate
   ```
3. Install the package and its dependencies:
   ```bash
   pip install .
   pip install -r requirements.txt
   ```

## Running Tests

Tests are written with `pytest`. After installing dependencies you can run:

```bash
pytest
```

If you want the tests to use the real authentication libraries instead of
the lightweight stubs provided in `tests/conftest.py`, install the
optional packages first:

```bash
pip install redis passlib[bcrypt] python-jose[cryptography]
```

You can also install both requirement files to match the CI environment:

```bash
pip install -r requirements-minimal.txt -r requirements-dev.txt
```

If the packages are missing, stub implementations found under `stubs/`
will activate automatically and may cause confusing test failures.

The GitHub Actions workflows (`.github/workflows/ci.yml` and `pr-tests.yml`) run these commands automatically whenever you push or open a pull request.

## Pre-commit Hooks

Install the development tools and enable the git hooks so code is automatically
formatted and linted. The hooks rely on packages from both requirement files:

```bash
pip install -r requirements-minimal.txt -r requirements-dev.txt
pre-commit install
```

Run all hooks manually with:

```bash
pre-commit run --all-files
```

## Optional Frontend

The `transcendental_resonance_frontend/` directory contains a NiceGUI-based UI. Follow its README to install `pip install -r transcendental_resonance_frontend/requirements.txt` and run the frontend if desired.
