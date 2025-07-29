"""Entry point for ``python -m transcendental_resonance_frontend``."""

from nicegui import ui

from .src import main as frontend_main


def run() -> None:
    """Launch the NiceGUI frontend."""
    # Ensure at least one element is created before starting
    ui.label("Launching frontend...")
    frontend_main.run_app()


if __name__ == "__main__":  # pragma: no cover - manual launch
    run()
