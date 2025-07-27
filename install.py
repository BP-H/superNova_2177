import os
import subprocess
import sys
from pathlib import Path
import venv
import shutil


def create_env(env_dir: Path) -> None:
    if not env_dir.exists():
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(env_dir)


def run(cmd):
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd)


def main():
    env_dir = Path('venv')
    create_env(env_dir)

    if os.name == 'nt':
        bin_dir = env_dir / 'Scripts'
    else:
        bin_dir = env_dir / 'bin'

    pip = bin_dir / ('pip.exe' if os.name == 'nt' else 'pip')

    # Upgrade pip then install requirements
    run([str(pip), 'install', '--upgrade', 'pip'])

    req = Path('requirements.txt')
    if req.exists():
        run([str(pip), 'install', '-r', str(req)])

    # Copy .env.example if .env doesn't exist
    example = Path('.env.example')
    target = Path('.env')
    if example.exists() and not target.exists():
        shutil.copy(example, target)
        print('Copied .env.example to .env')

    activation = 'venv\\Scripts\\activate' if os.name == 'nt' else 'source venv/bin/activate'
    print(f"Installation complete. Activate the environment with '{activation}'")


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)
