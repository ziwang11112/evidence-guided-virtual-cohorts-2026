"""Run or resume the development workflow through the model's final decision."""
import argparse
from pathlib import Path
import subprocess
import sys

from filelock import FileLock

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--article', required=True, type=Path)
    parser.add_argument('--case', required=True, help='Key in development_requests.json')
    parser.add_argument('--run', required=True, help='Opaque run identifier')
    args = parser.parse_args()
    if not args.run.isidentifier():
        raise ValueError('Use an opaque run identifier')
    author_args = ['--article', str(args.article.resolve()), '--case', args.case]
    folder = HERE / 'private' / args.run
    folder.mkdir(parents=True, exist_ok=True)
    with FileLock(str(folder / 'driver.lock'), timeout=0):
        for stage in ('design', 'build', 'trial', 'review', 'final'):
            authoring = stage in ('design', 'build', 'review')
            script = 'author_stage.py' if authoring else 'run_candidate_stage.py'
            command = [sys.executable, '-B', str(HERE / script), stage, '--run', args.run]
            subprocess.run(command + (author_args if authoring else []), check=True)


if __name__ == '__main__':
    main()
