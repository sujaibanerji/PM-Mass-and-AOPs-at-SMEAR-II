"""Headless equivalent of the visible one-click UI; current redraw or explicit r6 recompute."""
import argparse
from datetime import datetime,timezone
import html
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from release_io import HERE,configuration,prepare


def run(output=None,archive_dir=None,allow_network=True,historical=False,progress=print):
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output=Path(output).resolve() if output else HERE/'outputs'/stamp
    if output.exists():
        raise FileExistsError('Choose a fresh output root.')
    # Put archives and extracted inputs outside the downloadable results tree.
    runtime=prepare(output/'runtime',archive_dir,allow_network,progress)
    result=output/'results'
    command=[sys.executable,'-B',str(runtime/'codes/run_all.py'),'--data-dir',str(runtime/'data'),
             '--output-dir',str(result)]
    if historical:
        command.append('--historical-recompute')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg')
    with (output/'launcher.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen(command,cwd=runtime/'codes',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        for line in process.stdout:
            log.write(line); log.flush(); progress(line.rstrip())
        status=process.wait()
    if status:
        raise RuntimeError('Analysis failed; see launcher.log and job logs. No old-release fallback.')
    main=result/'python/main_manuscript'
    title='Do the PM mass and aerosol optical properties differ between plant-material-labelled and dust-event-associated filters at Hyytiälä?'
    gallery=['<!doctype html><meta charset="utf-8"><title>'+html.escape(title)+'</title>',
             '<h1>'+html.escape(title)+'</h1><p>Figures 2–8 redrawn from frozen saved inputs; Figure 1 is the exact supplied current workflow asset. Dust replay is Python-only. No new bootstrap in default mode.</p>']
    for n in range(1,9):
        gallery.append(f'<h2>Figure {n}</h2><img style="max-width:100%" src="python/main_manuscript/figure_{n}.png" alt="Figure {n}">')
    gallery.append('<p><a href="python/supporting_figures_supplementary_information/dust_audit/direct_P_minus_D.csv">Dust direct P−D effects CSV</a> · <a href="python/supporting_figures_supplementary_information/dust_audit/category_counts.csv">Dust counts CSV</a></p>')
    (result/'index.html').write_text('\n'.join(gallery),encoding='utf-8')
    # Exclude scratch renderer inputs/previews: exports contain results, not
    # another copy of immutable inputs or code/data archives.
    with zipfile.ZipFile(output/'results.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(result.rglob('*')):
            if p.is_file() and not {'saved_input_work','_render'}.intersection(p.parts) and p.name!='.run.lock':
                z.write(p,p.relative_to(result).as_posix())
    report=dict(release_id=configuration()['release_id'],status='passed',
                current_figures='7 saved-input redraws plus exact current workflow asset',
                dust='Python-only immutable-input numerical replay',historical_recomputed=historical,
                full_raw_data_rerun=False,cloud_tested_by_preparer=False,
                main_figures=8,results_zip='results.zip')
    (output/'launcher_verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    progress('Done: eight current figures and the dust diagnostic. Download results.zip before closing Binder.')
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path)
    p.add_argument('--archive-dir',type=Path,help='Local matching codes.zip and data.zip; never network fallback when supplied.')
    p.add_argument('--offline',action='store_true')
    p.add_argument('--historical-recompute',action='store_true')
    a=p.parse_args()
    run(a.output_dir,a.archive_dir,not a.offline,a.historical_recompute)


if __name__=='__main__':
    main()
