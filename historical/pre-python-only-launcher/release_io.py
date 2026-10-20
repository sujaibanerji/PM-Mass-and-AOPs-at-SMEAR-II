"""Integrity-checked, staged preparation of the three matching release archives."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen
import zipfile

KEYS = {'codes', 'data', 'additional_figures'}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative_path(root, name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError(f'Unsafe archive/manifest path: {name}')
    result = (Path(root) / name).resolve()
    if not result.is_relative_to(Path(root).resolve()):
        raise ValueError('Path outside destination')
    return result


def verify_archive(path, spec):
    if Path(path).stat().st_size != spec['bytes'] or digest(path) != spec['sha256']:
        raise ValueError(f'Archive integrity failed: {spec["filename"]}')


def safe_extract(archive, destination):
    with zipfile.ZipFile(archive) as z:
        seen = set()
        if sum(i.file_size for i in z.infolist()) > 10 * 1024**3:
            raise ValueError('Archive exceeds extraction limit')
        for entry in z.infolist():
            target = relative_path(destination, entry.filename)
            mode = stat.S_IFMT(entry.external_attr >> 16)
            if mode not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError('Archive links/special files are forbidden')
            identity = entry.filename.rstrip('/').casefold()
            if identity in seen:
                raise ValueError('Duplicate archive member')
            seen.add(identity)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(entry) as source, target.open('xb') as out:
                    shutil.copyfileobj(source, out, 1024 * 1024)


def verify_additional(root):
    manifest = json.loads((Path(root) / 'manifest.json').read_text(encoding='utf-8'))
    seen = set()
    for entry in manifest['files']:
        p = relative_path(root, entry['path'])
        if entry['path'] in seen or p.stat().st_size != entry['bytes'] or digest(p) != entry['sha256']:
            raise ValueError('Additional figure integrity failed')
        seen.add(entry['path'])
    for f in manifest['figures']:
        if f['asset'] not in seen:
            raise ValueError('Missing canonical additional asset')
    return manifest


def tree_hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(Path(root).rglob('*'))
            if p.is_file() and p.name != '.prepared.json' and '__pycache__' not in p.parts}


def prepared_paths(destination, identity):
    return dict({key: str((destination / key).resolve()) for key in sorted(KEYS)},
                root=str(destination.resolve()), identity=identity)


def prepare_release(config: Path, destination: Path, local_archives=None) -> dict:
    spec = json.loads(Path(config).read_text(encoding='utf-8'))
    archives = spec['archives']
    if set(archives) != KEYS or (local_archives is not None and set(local_archives) != KEYS):
        raise ValueError('All three archives are required')
    identity = dict(release_id=spec['release_id'], archives={k: {field: archives[k][field]
                     for field in ('bytes', 'sha256')} for k in sorted(KEYS)})
    destination = Path(destination).resolve()
    if destination.exists():
        marker = destination / '.prepared.json'
        if not marker.is_file():
            raise FileExistsError('Refusing unrelated existing destination')
        previous = json.loads(marker.read_text(encoding='utf-8'))
        if previous['identity'] != identity or tree_hashes(destination) != previous['files']:
            raise ValueError('Prepared release differs or has changed; use a fresh destination')
        verify_additional(destination / 'additional_figures')
        return prepared_paths(destination, identity)
    if local_archives is None and any(urlparse(a.get('url') or '').scheme != 'https'
                                       for a in archives.values()):
        raise ValueError('Set version-specific HTTPS URLs for all three archives, or supply all local ZIPs')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.prepare-', dir=destination.parent) as temporary:
        temp = Path(temporary)
        staged = temp / 'release'
        staged.mkdir()
        for key in sorted(KEYS):
            a = archives[key]
            if local_archives is not None:
                archive = Path(local_archives[key])
            else:
                archive = temp / (key + '.zip')
                with urlopen(a['url'], timeout=120) as response, archive.open('xb') as out:
                    if urlparse(response.geturl()).scheme != 'https':
                        raise ValueError('Download redirected away from HTTPS')
                    received = 0
                    while block := response.read(1024 * 1024):
                        received += len(block)
                        if received > a['bytes']:
                            raise ValueError('Download exceeds declared size')
                        out.write(block)
            verify_archive(archive, a)
            safe_extract(archive, staged / key)
        log = temp / 'package_checks.log'
        with log.open('w', encoding='utf-8') as out:
            result = subprocess.run([sys.executable, '-B', str(staged / 'codes' / 'package_checks.py'),
                '--data-dir', str(staged / 'data')], cwd=staged / 'codes', stdout=out, stderr=subprocess.STDOUT)
        if result.returncode:
            raise ValueError('Original package checks failed:\n' + log.read_text(encoding='utf-8'))
        verify_additional(staged / 'additional_figures')
        shutil.copyfile(log, staged / 'package_checks.log')
        marker = dict(identity=identity, files=tree_hashes(staged))
        (staged / '.prepared.json').write_text(json.dumps(marker, indent=2), encoding='utf-8')
        staged.rename(destination)
    return prepared_paths(destination, identity)
