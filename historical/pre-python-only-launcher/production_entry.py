"""Invoke the unchanged release launcher while preserving a symlinked venv."""
import argparse
import importlib.util
import os
from pathlib import Path
import sys


def execute_original(codes, argv):
    source = Path(codes) / 'run_all.py'
    spec = importlib.util.spec_from_file_location('_hyytiala_original_run_all', source)
    original = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(Path(codes)))
    try:
        spec.loader.exec_module(original)
        original_resolver = original.resolve_executable

        def preserve_environment(value):
            # Path.resolve() follows venv/bin/python to the base interpreter and
            # loses site-packages. An absolute path retains pyvenv.cfg discovery.
            if str(value) == sys.executable:
                return os.path.abspath(sys.executable)
            return original_resolver(value)

        original.resolve_executable = preserve_environment
        original.main(argv)
    finally:
        sys.path.pop(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codes-dir', type=Path, required=True)
    args, remaining = parser.parse_known_args()
    execute_original(args.codes_dir, remaining)
