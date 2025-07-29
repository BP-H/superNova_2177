"""Entry point for ``python -m transcendental_resonance_frontend``."""

from nicegui import ui

from .src import main


def run() -> None:
    """Launch the NiceGUI-based frontend."""
    # Ensure at least one element is created before starting the app
    ui.label("Launching Transcendental Resonance UI...")
    main.run_app()


if __name__ == "__main__":  # pragma: no cover - manual execution
    run()
