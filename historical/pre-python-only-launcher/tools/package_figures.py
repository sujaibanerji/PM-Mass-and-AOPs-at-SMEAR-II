"""Preserve reviewed historical figure bytes in a deterministic additive ZIP."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.audit_figures import sha256


def source_path(root, identity):
    kind, relative = identity.split(':', 1)
    p = PurePosixPath(relative)
    if kind != 'project' or p.is_absolute() or '..' in p.parts or '\\' in relative or ':' in relative:
        raise ValueError('Invalid relative project source')
    resolved = (Path(root) / relative).resolve()
    if not resolved.is_relative_to(Path(root).resolve()):
        raise ValueError('Source outside root')
    return resolved


def build_bundle(inventory_path: Path, source_root: Path, output_zip: Path) -> dict:
    inventory = json.loads(Path(inventory_path).read_text(encoding='utf-8'))
    if inventory.get('unresolved'):
        raise ValueError('Unresolved inventory')
    figures = [dict(f) for f in inventory['figures'] if f['regeneration'] == 'archived_image']
    files, members = [], {}
    for f in figures:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', f['id']):
            raise ValueError('Invalid figure ID')
        assets = [dict(source=f['canonical_source'], sha256=f['sha256'])] + f.get('formats', [])
        for i, asset in enumerate(assets):
            source = source_path(source_root, asset['source'])
            data = source.read_bytes()
            if hashlib.sha256(data).hexdigest() != asset['sha256']:
                raise ValueError(f'Source changed: {asset["source"]}')
            member = f'figures/{f["id"]}/{source.name}'
            if member in members:
                raise ValueError('Repeated bundle member')
            members[member] = data
            files.append(dict(path=member, bytes=len(data), sha256=asset['sha256'], source=asset['source']))
            if i == 0:
                f['asset'] = member
            else:
                asset['asset'] = member
        f['formats'] = assets[1:]
    manifest = dict(schema_version=1, figures=figures, files=files)
    manifest_data = (json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    output_zip = Path(output_zip)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_zip.with_suffix('.zip.partial')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(dict(members, **{'manifest.json': manifest_data}).items()):
                entry = zipfile.ZipInfo(name, date_time=(2026, 10, 18, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data)
        temporary.replace(output_zip)
    finally:
        temporary.unlink(missing_ok=True)
    return dict(bytes=output_zip.stat().st_size, sha256=sha256(output_zip),
                figure_count=len(figures), file_count=len(files),
                manifest_sha256=hashlib.sha256(manifest_data).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=Path('figure_inventory.json'))
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_bundle(args.inventory, args.source_root, args.output), indent=2))
