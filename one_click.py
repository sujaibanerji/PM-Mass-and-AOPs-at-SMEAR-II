"""A single deliberate button for the existing full Python production workflow."""
from contextlib import redirect_stdout, redirect_stderr
from contextvars import copy_context
from datetime import datetime, timezone
import html
import io
import json
import os
from pathlib import Path
import threading
import time
from urllib.parse import quote
import zipfile

import ipywidgets as widgets

from release_io import prepare_release
from reviewer import run_full, notebook_gallery


INTRO = '''<h1>Run the manuscript analysis</h1>
<p>This Python code accompanies the manuscript and its supplementary information.
Click <strong>Run full analysis</strong> below to recalculate the current analyses
and open the complete figure gallery. Historical figures retain their original methods and cohorts.</p>
<p><strong>Estimated calculation time: 10–30 minutes, depending on the Binder server.</strong>
Initial startup may take a few minutes. The first run downloads and verifies the supplied archives before calculation.
The calculation runs on Binder’s servers;
your internet speed mainly affects page loading and downloads.</p>
<p>The complete gallery contains 131 distinct figures and 282 image assets.
Download your results before leaving: Binder sessions are temporary.</p>'''


def file_url(path):
    prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/').rstrip('/')
    return prefix + '/files/' + quote(Path(path).as_posix())


class Progress(io.TextIOBase):
    def __init__(self, dashboard):
        self.dashboard = dashboard

    def write(self, text):
        if text:
            self.dashboard.logs.append_stdout(text)
            stages = {
                'python_supporting_MM': 'Calculating main-manuscript supporting analyses…',
                'python_supporting_SI': 'Calculating supplementary and size analyses…',
                'python_MM': 'Rendering main-manuscript figures…',
                'python_SI': 'Writing supplementary results…',
                'python_reference_check': 'Checking numerical results against the references…',
            }
            for name, label in stages.items():
                if 'START: ' + name in text:
                    self.dashboard.status.value = '<p><strong>' + label + '</strong></p>'
        return len(text)


class Dashboard:
    def __init__(self, *, config=Path('binder_release.json'), runtime=Path('runtime'),
                 outputs=Path('outputs'), runner=run_full):
        self.config, self.runtime, self.outputs = Path(config), Path(runtime), Path(outputs)
        self.runner = runner
        self.running = False
        self.lock = threading.Lock()
        self.button = widgets.Button(description='Run full analysis', button_style='primary',
                                     icon='play', layout=widgets.Layout(width='220px', height='42px'))
        self.status = widgets.HTML('<p>Ready. Click the button to begin.</p>')
        self.logs = widgets.Output(layout=widgets.Layout(max_height='280px', overflow='auto'))
        self.downloads = widgets.HTML('')
        self.gallery = widgets.HTML('', layout=widgets.Layout(width='100%'))
        progress = widgets.Accordion(children=[self.logs], selected_index=None)
        progress.set_title(0, 'Calculation log')
        self.view = widgets.VBox([widgets.HTML(INTRO), self.button, self.status, progress,
                                  self.downloads, self.gallery], layout=widgets.Layout(width='100%'))
        self.button.on_click(self.start)

    def start(self, _button):
        with self.lock:
            if self.running:
                return
            self.running = True
            self.button.disabled = True
        self.downloads.value = ''
        self.gallery.value = ''
        self.logs.clear_output()
        self.status.value = '<p><strong>Verifying the supplied archives…</strong></p>'
        context = copy_context()
        threading.Thread(target=context.run, args=(self.calculate,), daemon=True).start()

    def calculate(self):
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        output = self.outputs / ('production_' + started.strftime('%Y%m%dT%H%M%S%fZ'))
        try:
            stream = Progress(self)
            with redirect_stdout(stream), redirect_stderr(stream):
                prepared = prepare_release(self.config, self.runtime)
                result = self.runner(prepared, output, confirmed=True)
            self.status.value = '<p><strong>Preparing the gallery and downloads…</strong></p>'
            archive = output / 'analysis_tables_and_logs.zip'
            with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
                for path in sorted((output / 'analysis').rglob('*')):
                    if path.is_file():
                        z.write(path, path.relative_to(output).as_posix())
                for name in ('production.log', 'binder_production_wrapper.json'):
                    path = output / name
                    if path.is_file():
                        z.write(path, name)
            elapsed = time.monotonic() - clock
            record = dict(status='completed', started_utc=started.isoformat(),
                          finished_utc=datetime.now(timezone.utc).isoformat(), seconds=elapsed,
                          figures=len(result['figures']))
            (output / 'one_click_run.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
            self.gallery.value = notebook_gallery(output / 'gallery/index.html',
                                                 file_url(output / 'gallery') + '/')
            links = [(output/'all_figures.zip', 'Download all figures (ZIP)'),
                     (archive, 'Download analysis tables and logs (ZIP)')]
            self.downloads.value = '<p>' + ' · '.join(
                '<a download href="' + html.escape(file_url(path), quote=True) + '">' + label + '</a>'
                for path, label in links) + '</p>'
            self.status.value = (f'<p><strong>Complete: {len(result["figures"])} figures ready.</strong> '
                                 f'Calculation and packaging took {elapsed/60:.1f} minutes.</p>')
            self.button.description = 'Run full analysis again'
        except Exception as exc:
            self.status.value = ('<p><strong>Analysis failed.</strong> ' + html.escape(str(exc)) +
                                 ' Open the calculation log for details. Existing outputs have been preserved.</p>')
        finally:
            with self.lock:
                self.button.disabled = False
                self.running = False


def create_dashboard():
    return Dashboard()
