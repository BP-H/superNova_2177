# Development Setup

This repository targets **Python 3.12** and uses standard tooling for managing dependencies and tests.

## Prerequisites

1. Install Python 3.12.
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

The GitHub Actions workflows (`.github/workflows/ci.yml` and `pr-tests.yml`) run these commands automatically whenever you push or open a pull request.

## Pre-commit Hooks

Install the development tools and enable the git hooks so code is automatically formatted and linted:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

Run all hooks manually with:

```bash
pre-commit run --all-files
```

## Optional Frontend

The `transcendental-resonance-frontend/` directory contains a NiceGUI-based UI. Follow its README to install `pip install -r transcendental-resonance-frontend/requirements.txt` and run the frontend if desired.
