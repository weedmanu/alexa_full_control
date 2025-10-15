#!/usr/bin/env python3
"""
Render PlantUML .puml files locally to SVG using plantuml.jar or Docker.

Usage:
  python scripts/render_plantuml_local.py docs/diagrams/install_full_flow.puml

Behavior:
 - If plantuml.jar exists next to this script (or at PROJECT_ROOT/tools/plantuml.jar), it will be used.
 - Otherwise, if Docker is available, it will try to run the official plantuml docker image.
 - Otherwise, it prints clear installation instructions.
"""
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / 'tools'
JAR_PATHS = [PROJECT_ROOT / 'plantuml.jar', TOOLS_DIR / 'plantuml.jar']


def find_jar() -> Path | None:
    for p in JAR_PATHS:
        if p.exists():
            return p
    return None


def has_docker() -> bool:
    return shutil.which('docker') is not None


def render_with_jar(jar: Path, puml: Path, out: Path) -> int:
    cmd = [sys.executable, '-m', 'subprocess', '--help']
    # Use java -jar plantuml.jar -tsvg -pipe < file > out
    try:
        with puml.open('rb') as f_in, out.open('wb') as f_out:
            proc = subprocess.run(['java', '-jar', str(jar), '-tsvg', '-pipe'], input=f_in.read(), stdout=subprocess.PIPE)
            if proc.returncode != 0:
                print('plantuml.jar returned non-zero exit code')
                return proc.returncode
            f_out.write(proc.stdout)
            return 0
    except FileNotFoundError:
        print('Java not found. Please install Java (JRE) to use plantuml.jar')
        return 2


def render_with_docker(puml: Path, out: Path) -> int:
    # Use official plantuml docker image: plantuml/plantuml
    try:
        cmd = [
            'docker', 'run', '--rm', '-i',
            '-v', f"{puml.parent.resolve()}:/work",
            'plantuml/plantuml:plantuml', '-tsvg', '-pipe'
        ]
        with puml.open('rb') as f_in, out.open('wb') as f_out:
            proc = subprocess.run(cmd, input=f_in.read(), stdout=subprocess.PIPE)
            if proc.returncode != 0:
                print('Docker plantuml returned non-zero')
                return proc.returncode
            f_out.write(proc.stdout)
            return 0
    except FileNotFoundError:
        print('Docker not available')
        return 3


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/render_plantuml_local.py path/to/file.puml')
        sys.exit(1)

    puml = Path(sys.argv[1]).resolve()
    if not puml.exists():
        print('PUML file not found:', puml)
        sys.exit(2)

    out = puml.with_suffix('.svg')

    jar = find_jar()
    if jar:
        print('Using plantuml.jar at', jar)
        rc = render_with_jar(jar, puml, out)
        sys.exit(rc)

    if has_docker():
        print('Using Docker to render PlantUML')
        rc = render_with_docker(puml, out)
        sys.exit(rc)

    print('\nNo plantuml.jar found and Docker not available.')
    print('To render locally, either:')
    print('  1) Install Java (JRE) and download plantuml.jar:')
    print('       https://plantuml.com/download')
    print(f"     Place plantuml.jar in {PROJECT_ROOT} or {TOOLS_DIR}")
    print('  2) Install Docker and ensure `docker` is in PATH')
    print('\nAfter installing, re-run:')
    print(f'  python {Path(__file__).name} {puml.relative_to(PROJECT_ROOT)}')
    sys.exit(4)


if __name__ == "__main__":
    main()
