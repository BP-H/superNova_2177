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

Installing every dependency from `requirements-minimal.txt` and
`requirements-dev.txt` prevents these stubs from loading and keeps the tests
reliable.

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

Most editors will also respect the formatting settings in `.editorconfig` at the
repository root. It enforces UTF-8 encoding, LF newlines and four-space
indentation.

The pre-commit configuration runs `scripts/check_no_streamlit_py.py` to ensure
no `streamlit.py` file exists anywhere in the repository. This prevents
accidentally shadowing the real Streamlit package. The same check runs early in
the CI workflows.

## Optional Frontend

The `transcendental_resonance_frontend/` directory contains a NiceGUI-based UI. Follow its README to install `pip install -r transcendental_resonance_frontend/requirements.txt` and run the frontend if desired.

## Vote Registry Roadmap

The `vote_registry.py` module is under active development. Planned tasks include:

- OAuth or wallet-based identity linking for validators.
- Public frontend pages showing vote timelines per species.
- Real-time consensus graphs across divergent forks.

## Troubleshooting

If the Streamlit UI fails to start when running tests or the smoke test in the
CI pipeline, inspect `streamlit.log` for errors and confirm that port `8888` is
free. Both the `ci.yml` and `pr-tests.yml` workflows print this file on failure
and upload it as a build artifact named `streamlit-log-python-<version>`. After
any GitHub Actions run, download the artifact from the "Artifacts" section of
the run summary to review the full log. You can also expand the "Streamlit logs"
group in the job output to see its contents inline. Terminate any leftover
processes with:

```bash
pkill streamlit || true
```

Rerun the tests after addressing the issue.
