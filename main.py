import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


def process_xml(config_xml: str) -> str:

    # setup env
    venv_path = str(ROOT / '.venv' / 'Lib' / 'site-packages')

    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = venv_path + os.pathsep + env['PYTHONPATH']
    else:
        env['PYTHONPATH'] = venv_path

    # run process
    python_path = ROOT / '.venv' / 'Scripts' / 'python.exe'

    try:
        process = subprocess.run(
            [
                python_path,
                'run.py',
                '--config',
                config_xml,
            ],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
            text=True,
            check=True,
            cwd=ROOT,
            env=env,
        )
        return process.stdout.strip()

    except subprocess.CalledProcessError:
        raise


if __name__ == '__main__':
    result = process_xml(
        config_xml=r'<input>C:\Atom x64 3.3 (2025.11.14)\Temp\py_table.xml</input>',
    )
    print(result)
