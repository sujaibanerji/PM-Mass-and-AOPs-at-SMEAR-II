"""Load only the exact configured new archives; validate size, hash, paths and CRC."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import urllib.parse
import urllib.request
import zipfile

HERE=Path(__file__).resolve().parent
RESERVED={'CON','PRN','AUX','NUL'} | {f'{a}{n}' for a in ('COM','LPT') for n in range(1,10)}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def safe_parts(name):
    parts=tuple(name.rstrip('/').split('/'))
    if not parts or name.startswith('/') or '\\' in name or '\x00' in name:
        raise ValueError('Unsafe ZIP name: '+name)
    for p in parts:
        if p in ('','.','..') or ':' in p or p.endswith((' ','.')) or p.split('.')[0].upper() in RESERVED:
            raise ValueError('Unsafe ZIP component: '+name)
    return parts


def check_archive(path,record):
    path=Path(path)
    if path.stat().st_size!=record['bytes'] or sha(path)!=record['sha256']:
        raise ValueError('Archive size/SHA-256 mismatch: '+path.name+'; no fallback to an older release.')


def safe_extract(path,destination):
    destination=Path(destination).resolve()
    if destination.exists():
        raise FileExistsError('Extraction destination already exists.')
    with zipfile.ZipFile(path) as z:
        seen={}
        infos=z.infolist()
        if len(infos)>10000 or sum(i.file_size for i in infos)>3_000_000_000:
            raise ValueError('Unexpected archive expansion.')
        for info in infos:
            parts=safe_parts(info.filename)
            key='/'.join(parts).casefold()
            if key in seen or stat.S_ISLNK(info.external_attr>>16):
                raise ValueError('Duplicate/case-colliding or symlink ZIP entry.')
            seen[key]=info.is_dir()
            target=destination.joinpath(*parts).resolve()
            if not target.is_relative_to(destination):
                raise ValueError('Archive path escapes destination.')
        for key in seen:
            parent=key.rpartition('/')[0]
            while parent:
                if parent in seen and not seen[parent]:
                    raise ValueError('Archive file/directory collision.')
                parent=parent.rpartition('/')[0]
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failure.')
        destination.mkdir(parents=True)
        for info in infos:
            target=destination.joinpath(*safe_parts(info.filename))
            if info.is_dir():
                target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                with z.open(info) as src,target.open('xb') as dst:
                    shutil.copyfileobj(src,dst,1024*1024)


def configuration():
    config=json.loads((HERE/'binder_release.json').read_text(encoding='utf-8'))
    if config['release_id']!='binder-20261025-consistent-counts' or set(config['archives'])!={'codes','data'}:
        raise ValueError('Unexpected release configuration; no historical default is supported.')
    for kind,record in config['archives'].items():
        if record['filename']!=kind+'.zip' or not re.fullmatch('[0-9a-f]{64}',record['sha256']):
            raise ValueError('Malformed archive configuration.')
    return config


def prepare(runtime,archive_dir=None,allow_network=True,progress=print):
    config=configuration()
    runtime=Path(runtime).resolve()
    if runtime.exists():
        raise FileExistsError('Use a fresh runtime directory; no stale release is reused.')
    runtime.mkdir(parents=True)
    cache=runtime/'download_cache'
    cache.mkdir()
    for kind,record in config['archives'].items():
        progress('Preparing '+record['filename']+' ('+config['release_id']+')')
        locations=[Path(archive_dir)/record['filename']] if archive_dir else [HERE/record['filename'],HERE.parent/record['filename']]
        local=next((p for p in locations if p.is_file()),None)
        if local is None:
            if archive_dir or not allow_network:
                raise FileNotFoundError('Matching local archive missing: '+record['filename'])
            url=record.get('url')
            if not url or urllib.parse.urlparse(url).scheme!='https':
                raise ValueError('A published HTTPS archive URL must be configured first.')
            local=cache/record['filename']
            partial=cache/(record['filename']+'.part')
            request=urllib.request.Request(url,headers={'User-Agent':'Hyytiala-reviewer/'+config['release_id']})
            with urllib.request.urlopen(request,timeout=120) as src,partial.open('xb') as dst:
                downloaded=0
                for block in iter(lambda:src.read(1024*1024),b''):
                    downloaded+=len(block)
                    if downloaded>record['bytes']:
                        raise ValueError('Download exceeds pinned archive size.')
                    dst.write(block)
            check_archive(partial,record)
            partial.rename(local)
        check_archive(local,record)
        safe_extract(local,runtime/kind)
    marker=dict(release_id=config['release_id'],archives=config['archives'],size_sha256_CRC_paths_checked=True)
    (runtime/'prepared.json').write_text(json.dumps(marker,indent=2)+'\n',encoding='utf-8')
    return runtime
