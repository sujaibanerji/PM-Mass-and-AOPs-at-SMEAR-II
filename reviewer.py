"""Reviewer rendering, complete figure gallery and explicitly opted-in production."""
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import zipfile
from urllib.parse import urlsplit

from release_io import digest, relative_path, verify_additional

HERE = Path(__file__).resolve().parent
ZIP_DOWNLOAD_LINK = '<a href="../all_figures.zip" download>Download complete figure set</a> · '


def notebook_gallery(gallery: Path, base_url: str) -> str:
    """Display static gallery markup in the notebook origin; load images as files.

    Jupyter deliberately sandboxes downloaded HTML files. Its opaque origin can
    prevent authenticated image requests. A static srcdoc retains the notebook
    origin without altering server policy or embedding image bytes.
    """
    parts = urlsplit(base_url)
    if (not base_url.startswith('/') or base_url.startswith('//') or
            parts.scheme or parts.netloc or parts.query or parts.fragment or not base_url.endswith('/')):
        raise ValueError('Gallery base must be an absolute same-server directory path')
    page = Path(gallery).read_text(encoding='utf-8')
    page = page.replace('<meta charset="utf-8">',
        f'<base href="{html.escape(base_url, quote=True)}"><meta charset="utf-8">', 1)
    return ('<iframe title="Complete scientific figure gallery" '
            'sandbox="allow-same-origin allow-downloads" '
            'style="width:100%;height:850px;border:0" srcdoc="' +
            html.escape(page, quote=True) + '"></iframe>')


def estimate_origin(figure_id, regeneration, production):
    if regeneration == 'archived_image':
        return 'archived_image'
    if figure_id == 'main_1':
        return 'fixed_artwork'
    if production:
        return 'recomputed_production'
    if figure_id == 'main_7' or not figure_id.startswith('main_'):
        return 'saved_reference'
    return 'processed_observations_and_saved_tables'


def fresh(path):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=False)
    return path


def run_live(command, log, cwd=None, progress_directory=None):
    """Stream launcher/job messages to the notebook and retain the complete log."""
    env = dict(os.environ, PYTHONUNBUFFERED='1', PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg')
    with Path(log).open('x', encoding='utf-8') as out:
        with subprocess.Popen([str(x) for x in command], cwd=cwd, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding='utf-8', errors='replace', bufsize=1) as proc:
            stop = threading.Event()
            def watch():
                positions = {}
                def show():
                    for path in sorted(Path(progress_directory).glob('*.log')):
                        with path.open('r', encoding='utf-8', errors='replace') as stream:
                            stream.seek(positions.get(path, 0))
                            text = stream.read(6000)
                            # Long machine-readable reports remain complete in the
                            # original log; keep notebook output bounded.
                            stream.seek(0, 2)
                            positions[path] = stream.tell()
                        if text.strip():
                            print(f'[{path.stem}] {text.rstrip()}', flush=True)
                while not stop.wait(2):
                    show()
                show()
            watcher = threading.Thread(target=watch, daemon=True) if progress_directory else None
            if watcher:
                watcher.start()
            try:
                for line in proc.stdout:
                    print(line.rstrip(), flush=True)
                    out.write(line); out.flush()
                code = proc.wait()
            finally:
                stop.set()
                if watcher:
                    watcher.join()
    if code:
        raise RuntimeError(f'Calculation failed ({code}); read {log}')


def assemble(prepared, main, supporting, output, production=False):
    inventory = json.loads((HERE / 'figure_inventory.json').read_text(encoding='utf-8'))
    extra_root = Path(prepared['additional_figures'])
    extra = verify_additional(extra_root)
    extra_by_id = {f['id']: f for f in extra['figures']}
    figures = []
    for entry in inventory['figures']:
        f = dict(entry)
        f['estimate_origin'] = estimate_origin(f['id'], f['regeneration'], production)
        if f['regeneration'] == 'registered':
            f['reference_sha256'] = f['sha256']
            if production:
                f['scope'] = ('Production workflow from supplied processed observations; read original calculation and rendering scope manifests. Figure 1 remains fixed artwork.')
            filename = ('figure_' + f['id'].split('_')[-1] + '.png'
                        if f['id'].startswith('main_') else f['id'] + '.png')
            path = Path(main if f['id'].startswith('main_') else supporting) / filename
            if not path.is_file():
                raise ValueError(f'Missing registered figure: {f["id"]}')
            f['sha256'] = digest(path)
            f['path'] = str(path)
            f['formats'] = []
        else:
            asset = extra_by_id[f['id']]
            if asset['sha256'] != f['sha256']:
                raise ValueError('Inventory/bundle mismatch')
            f['path'] = str(relative_path(extra_root, asset['asset']))
            f['formats'] = [dict(a, path=str(relative_path(extra_root, a['asset'])))
                            for a in asset.get('formats', [])]
        figures.append(f)
    return dict(schema_version=1, figures=figures,
                expected_ids=[f['id'] for f in inventory['figures']],
                production=production, output=str(output),
                provenance_paths=[str(Path(main) / 'run_manifest.json'),
                                  str(Path(supporting) / 'supporting_figure_manifest.json')],
                path_redactions={str(Path(prepared['root']).resolve()): 'runtime',
                                 str(Path(output).resolve()): 'results',
                                 str(HERE): 'launcher', sys.executable: 'python'})


def render_saved(prepared: dict, output: Path) -> dict:
    output = fresh(output)
    codes, data = Path(prepared['codes']), Path(prepared['data'])
    main, support = output / 'current/main_manuscript', output / 'current/supporting'
    print('Rendering seven main figures from processed observations and saved tables.', flush=True)
    run_live([sys.executable, '-B', codes / 'python_codes/main_manuscript.py',
              '--data-dir', data, '--output-dir', main], output / 'render_main.log')
    snippet = ('import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); '
               'from supporting_plots import render_supporting; '
               'render_supporting(Path(sys.argv[2]),Path(sys.argv[3]))')
    run_live([sys.executable, '-B', '-c', snippet, codes / 'python_codes',
              data / 'reference', support], output / 'render_supporting.log')
    manifest = assemble(prepared, main, support, output)
    build_gallery(manifest, output / 'gallery')
    export_results(manifest, output / 'all_figures.zip')
    return manifest


def run_full(prepared: dict, output: Path, *, confirmed: bool = False) -> dict:
    if confirmed is not True:
        raise ValueError('Full analysis requires confirmed=True; normal Run All skips it')
    output = fresh(output)
    codes, data = Path(prepared['codes']), Path(prepared['data'])
    analysis = output / 'analysis'  # Original launcher reserves this directory itself.
    wrapper_record = output / 'binder_production_wrapper.json'
    wrapper_record.write_text(json.dumps(dict(wrapper_sha256=digest(HERE / 'production_entry.py'),
        purpose='Keep the active virtual-environment interpreter for original launcher child jobs; scientific sources unchanged',
        python=sys.executable), indent=2), encoding='utf-8')
    print(f'Production log: {output / "production.log"}; per-job logs: {analysis}/*.log', flush=True)
    run_live([sys.executable, '-B', HERE / 'production_entry.py', '--codes-dir', codes, '--data-dir', data,
              '--output-dir', analysis, '--language', 'python', '--all-methods',
              '--size-bootstrap', '--native-size-bootstrap'], output / 'production.log',
              progress_directory=analysis)
    jobs = json.loads((analysis / 'run_all_manifest.json').read_text(encoding='utf-8'))
    if jobs['status'] != 'completed_requested_jobs_with_scope_limits' or any(
            j.get('exit_code') != 0 for j in jobs['jobs']):
        raise ValueError('Production jobs did not all complete')
    reference = analysis / 'python_reference_check.json'
    if not reference.is_file():
        raise ValueError('Production numerical reference report missing')
    manifest = assemble(prepared, analysis / 'python/main_manuscript',
                        analysis / 'python/supporting_main_manuscript/supporting_figures', output, True)
    manifest['provenance_paths'] += [str(reference), str(analysis / 'run_all_manifest.json'), str(wrapper_record)]
    build_gallery(manifest, output / 'gallery')
    export_results(manifest, output / 'all_figures.zip')
    return manifest


def build_gallery(manifest: dict, output: Path) -> Path:
    figures = manifest['figures']
    ids = [f['id'] for f in figures]
    if len(ids) != len(set(ids)) or set(ids) != set(manifest['expected_ids']):
        raise ValueError('Incomplete or repeated figure inventory')
    for f in figures:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', f['id']):
            raise ValueError('Unsafe figure identity')
        for asset in [f] + f.get('formats', []):
            if digest(asset['path']) != asset['sha256']:
                raise ValueError('Missing or changed gallery asset')
    output = fresh(output)
    public = dict(schema_version=1, production=manifest.get('production', False), figures=[], files=[])
    cards = []
    esc = lambda x: html.escape(str(x), quote=True)
    for f in figures:
        entry = {k: v for k, v in f.items() if k not in ('path', 'formats')}
        links = []
        for i, asset in enumerate([f] + f.get('formats', [])):
            source = Path(asset['path'])
            relative = f'figures/{f["id"]}/{source.name}'
            target = relative_path(output, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError('Repeated gallery asset')
            shutil.copyfile(source, target)
            public['files'].append(dict(path=relative, sha256=digest(target), bytes=target.stat().st_size))
            links.append(f'<a download href="{esc(relative)}">{esc(source.suffix[1:].upper())}</a>')
            if i == 0:
                entry['asset'] = relative
            else:
                entry.setdefault('formats', []).append(dict(asset=relative, sha256=asset['sha256']))
        public['figures'].append(entry)
        cards.append(f'<article data-group="{esc(f["group"])}"><h2>{esc(f["title"])}</h2>'
            f'<p>{esc(f["group"])} · {esc(f["id"])} · <strong>{esc(f["estimate_origin"].replace("_", " "))}</strong></p>'
            f'<p>{esc(f["scope"])}</p><a href="{esc(entry["asset"])}">'
            f'<img loading="lazy" src="{esc(entry["asset"])}" alt="{esc(f["title"])}"></a>'
            f'<p>Download: {" · ".join(links)}</p><details><summary>Source and scope</summary>'
            f'<pre>{esc(json.dumps(entry, indent=2, ensure_ascii=False))}</pre></details></article>')
    for i, source in enumerate(manifest.get('provenance_paths', [])):
        text = Path(source).read_text(encoding='utf-8')
        for old, replacement in manifest.get('path_redactions', {}).items():
            text = text.replace(old.replace('\\', '\\\\'), replacement).replace(old, replacement)
        target = output / 'provenance' / f'{i+1}_{Path(source).name}'
        target.parent.mkdir(exist_ok=True)
        target.write_text(text, encoding='utf-8')
    scope_notice = ('Current production estimates have been recalculated. '
                    'Figure 1 is fixed artwork; historical figures remain archived.'
                    if manifest.get('production', False) else
                    'Saved-reference intervals have not been recalculated.')
    page = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" '
        'content="width=device-width, initial-scale=1"><title>Hyytiälä figure gallery</title>'
        '<style>body{font:17px/1.5 system-ui;max-width:1100px;margin:2em auto;padding:0 1em;'
        'color:#17314a}article{border-top:1px solid #ccd;padding:1em 0}img{max-width:100%;height:auto}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}a{color:#16577a}</style>'
        f'<h1>Hyytiälä figure gallery</h1><p>{len(figures)} distinct scientific figures. '
        'Historical figures retain their original methods and conventions. '
        f'{scope_notice} Click an image for full resolution.</p>'
        f'<p>{ZIP_DOWNLOAD_LINK}'
        '<a href="manifest.json">Figure manifest</a></p>' + ''.join(cards) + '</html>')
    (output / 'index.html').write_text(page, encoding='utf-8')
    (output / 'manifest.json').write_text(json.dumps(public, indent=2, ensure_ascii=False), encoding='utf-8')
    manifest['gallery_root'] = str(output)
    return output / 'index.html'


def export_results(manifest: dict, output_zip: Path) -> Path:
    root = Path(manifest['gallery_root'])
    if Path(output_zip).resolve().is_relative_to(root.resolve()):
        raise ValueError('Place the result ZIP beside the gallery, outside its asset directory')
    public = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    for f in public['files']:
        if digest(relative_path(root, f['path'])) != f['sha256']:
            raise ValueError('Changed result before export')
    with zipfile.ZipFile(output_zip, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():
                relative = p.relative_to(root).as_posix()
                if relative == 'index.html':
                    page = p.read_text(encoding='utf-8').replace(ZIP_DOWNLOAD_LINK, '', 1)
                    z.writestr(relative, page)
                else:
                    z.write(p, relative)
    return Path(output_zip)
