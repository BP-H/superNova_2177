"""Launch the Transcendental Resonance NiceGUI app."""

from .src.pages import *  # noqa: F401,F403 - register page decorators
from .src.main import run_app  # provides the run loop and additional setup

if __name__ == "__main__":
    run_app()
