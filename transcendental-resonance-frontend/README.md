# Transcendental Resonance Frontend

A minimalist social metaverse UI built with [NiceGUI](https://nicegui.io/) for interacting with the Transcendental Resonance protocol. This repository contains the modular front-end split from a single monolithic file.

## Setup

```bash
if [ -f requirements.lock ]; then
  pip install -r requirements.lock
else
  pip install -r requirements.txt
fi
nicegui src/main.py
```

### Demo mode

To explore the UI without a running backend, load the bundled sample data and
mock API calls:

```bash
python -m transcendental_resonance_frontend.demo
```

This command starts the app using data from `src/utils/sample_data/`.

Replace the backend URL with the `BACKEND_URL` environment variable if your API is not running on `http://localhost:8000`.

## Structure

- `src/pages/` – individual UI pages (login, profile, VibeNodes, etc.)
- `src/utils/` – shared utilities for API calls and styling
- `src/main.py` – entry point registering pages and launching the app
- `tests/` – pytest-based unit tests

## Notes

This UI is mobile-first with a futuristic aesthetic (dark mode and neon accents). A theme toggle is built in so you can switch between light and dark palettes. Future improvements include real-time notifications and internationalization.
