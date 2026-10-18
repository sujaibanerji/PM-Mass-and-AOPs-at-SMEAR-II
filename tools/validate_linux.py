"""Run acceptance checks with an already provisioned Linux Python environment."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from release_io import digest, prepare_release, relative_path
from reviewer import render_saved, run_full


def check_gallery(root):
    from PIL import Image
    manifest = json.loads((root / 'gallery/manifest.json').read_text(encoding='utf-8'))
    expected = json.loads((HERE / 'figure_inventory.json').read_text(encoding='utf-8'))
    assert {f['id'] for f in manifest['figures']} == {f['id'] for f in expected['figures']}
    for f in manifest['files']:
        assert digest(relative_path(root / 'gallery', f['path'])) == f['sha256']
    for f in manifest['figures']:
        with Image.open(relative_path(root / 'gallery', f['asset'])) as im:
            im.load()
            assert min(im.size) > 0
    with zipfile.ZipFile(root / 'all_figures.zip') as z:
        assert z.testzip() is None
        for f in manifest['files']:
            import hashlib
            assert hashlib.sha256(z.read(f['path'])).hexdigest() == f['sha256']
    return dict(figure_count=len(manifest['figures']), asset_count=len(manifest['files']),
                result_zip_bytes=(root / 'all_figures.zip').stat().st_size)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=HERE / 'binder_release.json')
    p.add_argument('--destination', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--codes-zip', type=Path, required=True)
    p.add_argument('--data-zip', type=Path, required=True)
    p.add_argument('--figures-zip', type=Path, required=True)
    p.add_argument('--full', action='store_true', help='Explicitly run the long production calculation')
    args = p.parse_args()
    if platform.system() != 'Linux' or sys.version_info[:3] != (3, 12, 14):
        p.error('Run this check under Linux Python 3.12.14')
    report = dict(status='running', python=sys.version, platform=platform.platform(),
                  actual_binder_tested=False, production_requested=args.full, packages={})
    start = time.monotonic()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    try:
        for line in (HERE / '.binder/requirements.txt').read_text().splitlines():
            if '==' in line:
                name, version = line.split('==')
                actual = importlib.metadata.version(name)
                assert actual == version, (name, version, actual)
                report['packages'][name] = actual
        subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=HERE, check=True)
        archives = dict(codes=args.codes_zip, data=args.data_zip, additional_figures=args.figures_zip)
        print('Preparing matching archives on the native Linux filesystem.', flush=True)
        prepared = prepare_release(args.config, args.destination, archives)
        report['archive_identity'] = prepared['identity']
        print('Verified release; starting ' + ('production' if args.full else 'saved-input rendering'), flush=True)
        if args.full:
            run_full(prepared, args.output, confirmed=True)
        else:
            render_saved(prepared, args.output)
        report.update(check_gallery(args.output))
        report['source_archives_after'] = {k: digest(path) for k, path in archives.items()}
        assert all(report['source_archives_after'][k] == prepared['identity']['archives'][k]['sha256'] for k in archives)
        report['status'] = 'passed'
    except Exception as error:
        report.update(status='failed', error=repr(error))
        raise
    finally:
        report['seconds'] = time.monotonic() - start
        report['peak_child_rss_kib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
