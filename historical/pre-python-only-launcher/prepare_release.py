"""Prepare verified matching archives, locally or from configured public URLs."""
import argparse
import json
from pathlib import Path
from release_io import prepare_release

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=Path('binder_release.json'))
    p.add_argument('--destination', type=Path, default=Path('runtime'))
    for name in ('codes', 'data', 'figures'):
        p.add_argument(f'--{name}-zip', type=Path)
    args = p.parse_args()
    values = [args.codes_zip, args.data_zip, args.figures_zip]
    if any(values) and not all(values):
        p.error('Local mode requires --codes-zip, --data-zip and --figures-zip together')
    local = dict(zip(('codes', 'data', 'additional_figures'), values)) if all(values) else None
    print(json.dumps(prepare_release(args.config, args.destination, local), indent=2))
