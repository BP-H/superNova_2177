import os
import sys
import shutil
import subprocess

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


def main() -> None:
    env_created = ensure_env()

    pip = pip_cmd()
    subprocess.check_call(pip + ['install', '--upgrade', 'pip'])
    subprocess.check_call(pip + ['install', 'supernova-2177'])

    if os.path.isfile('.env.example') and not os.path.isfile('.env'):
        shutil.copy('.env.example', '.env')
        print('Copied .env.example to .env')

    print('Installation complete.')
    if env_created:
        if os.name == 'nt':
            activate = f'{ENV_DIR}\\Scripts\\activate'
        else:
            activate = f'source {ENV_DIR}/bin/activate'
        print(f'Activate the environment with "{activate}"')
    print('Set SECRET_KEY in the environment or the .env file before running the app.')


if __name__ == '__main__':
    main()
