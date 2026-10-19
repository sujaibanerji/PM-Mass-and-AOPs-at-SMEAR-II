"""Package only the reviewed launcher snapshot, never local development history."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    '.gitattributes', '.gitignore', '.binder/environment.yml', '.binder/requirements.txt', '.binder/ui-requirements.txt', '.binder/postBuild',
    'README.md', 'VALIDATION.md', 'ONLINE_VALIDATION.json', 'FULL_ANALYSIS_VALIDATION.json', 'ONE_CLICK_VALIDATION.json', 'SCOPE_VALIDATION.json',
    'binder_release.json', 'figure_inventory.json', 'figure_exclusions.csv',
    'release_io.py', 'prepare_release.py', 'production_entry.py', 'reviewer.py', 'Start_here.ipynb', 'one_click.py', 'One_click.ipynb',
    'audit/README.md', 'audit/scope_revision.json', 'audit/renderer_artwork.diff', 'audit/selection_decisions.json', 'audit/pdf_pages.json',
    'tools/audit_figures.py', 'tools/package_figures.py', 'tools/package_launcher.py', 'tools/validate_linux.py',
    'tests/test_figure_audit.py', 'tests/test_figure_bundle.py', 'tests/test_production_entry.py',
    'tests/test_release_io.py', 'tests/test_reviewer.py', 'tests/test_one_click.py',
    'docs/superpowers/specs/2026-10-18-binder-launcher-design.md',
    'docs/superpowers/plans/2026-10-18-binder-launcher.md',
)


def build_launcher(root, output):
    members = {name: (Path(root) / name).read_bytes() for name in FILES}
    markers = [b'C:' + b'/Users/', b'C:' + bytes([92]) * 2 + b'Users' + bytes([92]) * 2,
               b'/mnt/c/' + b'Users/']
    for name, payload in members.items():
        if any(marker in payload for marker in markers):
            raise ValueError(f'Local machine path in publishable file: {name}')
    manifest = dict(schema_version=1, files=[dict(path=name, bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest()) for name, data in sorted(members.items())])
    members['launcher_manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.zip.partial')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(members.items()):
                info = zipfile.ZipInfo(name, (2026, 10, 18, 0, 0, 0))
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100755 if name == '.binder/postBuild' else 0o100644) << 16
                z.writestr(info, data)
        with zipfile.ZipFile(temporary) as z:
            if z.testzip() is not None or set(z.namelist()) != set(members):
                raise ValueError('Launcher archive membership/CRC failure')
            for name, data in members.items():
                if z.read(name) != data:
                    raise ValueError('Launcher member byte mismatch')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return dict(bytes=output.stat().st_size, sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                file_count=len(members))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(build_launcher(args.root, args.output), indent=2))
