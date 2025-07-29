"""Entry point for ``python -m transcendental_resonance_frontend``."""

from nicegui import ui


def run() -> None:
    """Launch the NiceGUI interface."""
    ui.label("Loading UI...")
    from .src.main import run_app
    run_app()


if __name__ == "__main__":
    run()
