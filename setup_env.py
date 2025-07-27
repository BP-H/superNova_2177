import os
import sys
import shutil
import subprocess
import argparse
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
        print(f'Creating virtual environment in {ENV_DIR}...')
        subprocess.check_call([sys.executable, '-m', 'venv', ENV_DIR])
        return True
    return False


def pip_cmd() -> list:
    if in_virtualenv():
        return [sys.executable, '-m', 'pip']
    return [venv_bin('pip')]


def run_app() -> None:
    """Launch the backend API using the environment's Python."""
    python_exe = sys.executable if in_virtualenv() else venv_bin('python')
    subprocess.check_call([python_exe, 'superNova_2177.py'])


def build_web_ui(pip: list) -> None:
    """Install UI deps and build the NiceGUI frontend."""
    ui_reqs = Path('transcendental-resonance-frontend') / 'requirements.txt'
    if ui_reqs.is_file():
        subprocess.check_call(pip + ['install', '-r', str(ui_reqs)])
    ui_script = Path('transcendental-resonance-frontend') / 'src' / 'main.py'
    nicegui = [venv_bin('nicegui')] if not in_virtualenv() else ['nicegui']
    subprocess.check_call(nicegui + ['build', str(ui_script)])


def main() -> None:
    parser = argparse.ArgumentParser(description='Set up the environment')
    parser.add_argument('--run-app', action='store_true', help='start the API after installation')
    parser.add_argument('--build-ui', action='store_true', help='build the web UI after installation')
    args = parser.parse_args()

    env_created = ensure_env()

    pip = pip_cmd()
    subprocess.check_call(pip + ['install', '--upgrade', 'pip'])
    subprocess.check_call(pip + ['install', '-r', 'requirements.txt'])
    subprocess.check_call(pip + ['install', '-e', '.'])

    if os.path.isfile('.env.example') and not os.path.isfile('.env'):
        shutil.copy('.env.example', '.env')
        print('Copied .env.example to .env')

    if args.build_ui:
        build_web_ui(pip)

    print('Installation complete.')
    if env_created:
        if os.name == 'nt':
            activate = f'{ENV_DIR}\\Scripts\\activate'
        else:
            activate = f'source {ENV_DIR}/bin/activate'
        print(f'Activate the environment with "{activate}"')
    print('Set SECRET_KEY in the environment or the .env file before running the app.')

    if args.run_app:
        run_app()


if __name__ == '__main__':
    main()
