# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import os
import sys
import shutil
import subprocess
import argparse
import logging
import importlib.util
from pathlib import Path

ENV_DIR = 'venv'


def in_virtualenv() -> bool:
    return sys.prefix != getattr(sys, 'base_prefix', sys.prefix)


def venv_bin(path: str) -> str:
    return os.path.join(ENV_DIR, 'Scripts' if os.name == 'nt' else 'bin', path)


def ensure_env() -> bool:
    """Create the virtual environment if not already active. Returns True if a
    new environment was created."""
    if in_virtualenv():
        return False
    if not os.path.isdir(ENV_DIR):
        logging.info('Creating virtual environment in %s...', ENV_DIR)
        try:
            subprocess.check_call([sys.executable, '-m', 'venv', ENV_DIR])
        except subprocess.CalledProcessError as exc:
            logging.error('Failed to create virtual environment: %s', exc)
            logging.error('Ensure the venv module is available and you have write permissions.')
            raise
        return True
    return False


def pip_cmd() -> list:
    if in_virtualenv():
        return [sys.executable, '-m', 'pip']
    return [venv_bin('pip')]


def run_app() -> None:
    """Launch the backend API using the environment's Python."""
    python_exe = sys.executable if in_virtualenv() else venv_bin('python')
    try:
        subprocess.check_call([python_exe, 'superNova_2177.py'])
    except subprocess.CalledProcessError as exc:
        logging.error('Failed to start the API: %s', exc)
        logging.error('Verify that dependencies are installed and try again.')
        raise


def run_ui() -> None:
    """Launch the Streamlit UI using the environment's Python."""
    python_exe = sys.executable if in_virtualenv() else venv_bin('python')
    if importlib.util.find_spec('streamlit') is None:
        logging.error('Streamlit is not installed. Install it with "pip install streamlit" and try again.')
        return
    try:
        subprocess.check_call([
            python_exe,
            '-m',
            'streamlit',
            'run',
            'ui.py',
            '--server.port',
            '8888',
        ])
    except subprocess.CalledProcessError as exc:
        logging.error('Failed to launch the Streamlit UI: %s', exc)
        logging.error('Ensure Streamlit is installed and functioning correctly.')
        raise


def build_frontend(pip: list) -> None:
    """Install UI deps and build the Transcendental Resonance frontend."""
    frontend_dir = Path('transcendental_resonance_frontend')
    ui_reqs = frontend_dir / 'requirements.txt'
    if ui_reqs.is_file():
        try:
            subprocess.check_call(pip + ['install', '-r', str(ui_reqs)])
        except subprocess.CalledProcessError as exc:
            logging.error('Failed to install UI dependencies: %s', exc)
            logging.error('Check your internet connection and try again.')
            raise
    ui_script = frontend_dir / 'src' / 'main.py'
    nicegui = [venv_bin('nicegui')] if not in_virtualenv() else ['nicegui']
    try:
        subprocess.check_call(nicegui + ['build', str(ui_script)])
    except subprocess.CalledProcessError as exc:
        logging.error('Failed to build the frontend: %s', exc)
        logging.error('Ensure Node.js and NiceGUI are properly installed.')
        raise


def main() -> None:
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 or newer is required.")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description='Set up the environment')
    parser.add_argument('--run-app', action='store_true', help='start the API after installation')
    parser.add_argument(
        '--build-ui',
        action='store_true',
        help='build the Transcendental Resonance frontend after installation',
    )
    parser.add_argument('--launch-ui', action='store_true', help='start the Streamlit UI after installation')
    parser.add_argument('--locked', action='store_true',
                        help='install dependencies from requirements.lock')
    args = parser.parse_args()

    env_created = ensure_env()

    pip = pip_cmd()
    try:
        subprocess.check_call(pip + ['install', '--upgrade', 'pip'])
        req_file = 'requirements.lock' if args.locked and os.path.isfile('requirements.lock') else 'requirements.txt'
        subprocess.check_call(pip + ['install', '-r', req_file])
        subprocess.check_call(pip + ['install', '-e', '.'])
    except subprocess.CalledProcessError as exc:
        logging.error('Dependency installation failed: %s', exc)
        logging.error('Check your internet connection and ensure pip is available.')
        raise

    if os.path.isfile('.env.example') and not os.path.isfile('.env'):
        shutil.copy('.env.example', '.env')
        print('Copied .env.example to .env')

    if args.build_ui:
        build_frontend(pip)

    print('Installation complete.')
    if env_created:
        activate_script = Path(ENV_DIR) / (
            "Scripts/activate" if os.name == "nt" else "bin/activate"
        )
        instruction = (
            str(activate_script)
            if os.name == "nt"
            else f"source {activate_script}"
        )
        print(f'Activate the environment with "{instruction}"')
    print('Set SECRET_KEY in the environment or the .env file before running the app.')

    if args.run_app:
        try:
            run_app()
        except subprocess.CalledProcessError:
            logging.error('Failed to run the application.')
            logging.error('Resolve the errors above and re-run with --run-app.')

    if args.launch_ui:
        try:
            run_ui()
        except subprocess.CalledProcessError:
            logging.error('Failed to launch the UI.')
            logging.error('Resolve the errors above and re-run with --launch-ui.')


if __name__ == '__main__':
    main()
