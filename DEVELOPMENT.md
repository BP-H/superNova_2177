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
   if [ -f requirements.lock ]; then
       pip install -r requirements.lock
   else
       pip install -r requirements.txt
   fi
   ```

## Running Tests

Tests are written with `pytest`. After installing dependencies you can run:

```bash
pytest
```

The GitHub Actions workflows (`.github/workflows/ci.yml` and `pr-tests.yml`) run these commands automatically whenever you push or open a pull request.

## Optional Frontend

The `transcendental-resonance-frontend/` directory contains a NiceGUI-based UI. Follow its README to install dependencies (using `requirements.lock` if present) and run the frontend if desired.
