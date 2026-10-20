"""Automatic default once per kernel; explicit retry and optional later reruns."""
import html
import os
from contextvars import copy_context
from threading import Lock,Thread
import traceback
from urllib.parse import quote
import ipywidgets as widgets
from IPython.display import display,HTML
from launcher import HERE,run
from release_io import configuration

INSTRUCTIONS=('Click the Binder link once, then wait. Everything will start automatically. '
              'Keep the tab open; do not click Run, change settings, or refresh the page. '
              'The figures and download links will appear when processing finishes.')

# Re-execution/re-rendering reuses this module. Preserve the controller even
# across explicit module reloads in the same kernel; a new kernel is a new run.
if '_SESSION' not in globals():
    _SESSION=None
    _SESSION_LOCK=Lock()


class Session:
    def __init__(self):
        self.lock=Lock(); self.state='idle'; self.last_historical=False
        self.status=widgets.HTML(value='<p>Starting automatically. Keep this tab open.</p>')
        self.output=widgets.Output()
        self.links=widgets.HTML(value='')
        self.option=widgets.Checkbox(value=False,disabled=True,
            description='Also recompute historical r6 processed-input analysis (slower)',
            indent=False,layout=widgets.Layout(width='95%'))
        self.button=widgets.Button(description='Optional: run again with selected option',
            disabled=True,layout=widgets.Layout(width='340px'))
        self.advanced=widgets.VBox([self.option,self.button],layout=widgets.Layout(display='none'))
        self.retry=widgets.Button(description='Retry failed run',button_style='warning',
                                  disabled=True,layout=widgets.Layout(display='none'))
        self.button.on_click(lambda _:self.start(self.option.value,'manual'))
        self.retry.on_click(lambda _:self.start(self.last_historical,'retry'))
        self.panel=widgets.VBox([self.status,self.output,self.links,self.retry,self.advanced])

    def start(self,historical=False,source='automatic'):
        with self.lock:
            required={'automatic':'idle','manual':'succeeded','retry':'failed'}[source]
            if self.state!=required:
                return  # Includes already-queued double clicks and re-renders.
            self.state='running'; self.last_historical=bool(historical)
            self.button.disabled=True; self.option.disabled=True; self.retry.disabled=True
            self.advanced.layout.display='none'; self.retry.layout.display='none'
            self.links.value=''
            mode='historical + current' if historical else 'current figures + dust audit'
            self.status.value=f'<p><b>Processing {mode}.</b> Keep the tab open; no action is needed.</p>'
            self.output.append_stdout('Starting '+mode+'; first build/downloads can take several minutes.\n')
        try:
            context=copy_context()
            Thread(target=lambda:context.run(self.execute),daemon=True).start()
        except Exception:
            self.failed()

    def failed(self):
        self.output.append_stderr(traceback.format_exc())
        with self.lock:
            self.status.value=('<p><b>Processing failed.</b> Details are above. No old release or saved-output '
                               'fallback was substituted. After resolving the problem, use Retry failed run. '
                               'There is no automatic retry; do not refresh.</p>')
            self.retry.layout.display=''; self.retry.disabled=False
            self.state='failed'

    def execute(self):
        try:
            folder=run(historical=self.last_historical,
                       progress=lambda line:self.output.append_stdout(str(line)+'\n'))
            rel=folder.relative_to(HERE).as_posix()
            prefix=os.environ.get('JUPYTERHUB_SERVICE_PREFIX','/').rstrip('/')
            url=html.escape(prefix+'/files/'+quote(rel)+'/',quote=True)
            gallery=(f'<p><a href="{url}results.zip" download>Download all results (ZIP)</a> · '
                     f'<a href="{url}results/index.html" target="_blank">Open gallery separately</a></p>')
            gallery+=''.join(f'<h3>Figure {n}</h3><img style="max-width:100%" '
                f'src="{url}results/python/main_manuscript/figure_{n}.png" alt="Figure {n}">'
                for n in range(1,9))
            with self.lock:
                self.links.value=gallery
                self.status.value='<p><b>Processing finished.</b> Figures and downloads are below. No further action is required.</p>'
                self.advanced.layout.display=''; self.button.disabled=False; self.option.disabled=False
                self.state='succeeded'
        except Exception:
            self.failed()


def show():
    global _SESSION
    config=configuration()
    display(HTML('<h1>Do the PM mass and aerosol optical properties differ between plant-material-labelled and dust-event-associated filters at Hyytiälä?</h1>'
      '<p><b>'+INSTRUCTIONS+'</b></p>'
      '<p>The initial Binder build and archive downloads can take several minutes. '
      'Progress appears here once this page has loaded.</p>'
      '<p><b>Version: '+html.escape(config.get('release_tag',config['release_id']))+'</b>. Archives are size- and SHA-256-pinned; '
      'unavailable new archives cause an error, never an old-release fallback.</p>'
      '<p><b>Automatic default:</b> redraw current Figures 2–8 from frozen saved/processed inputs; '
      'copy exact workflow Figure 1; recompute overlap, counts, medians and Cliff effects from the '
      'immutable dust snapshot. Saved uncertainty intervals are not recalculated. No original-instrument-data reconstruction.</p>'
      '<p>After success, optional manual controls can rerun the historical r6 processed-input analysis '
      '(5,000/2,000 draws), followed by the same current saved-input figures. Historical outputs are separate; '
      'changed settings do not flow into the frozen snapshots. No extra action is needed for the default results.</p>'
      '<p>Python performs the rendering and dust replay. Julia wrappers are shared-Python dispatch, not independent '
      'new uncertainty/dust validation. Download results before leaving: Binder storage is temporary.</p>'))
    with _SESSION_LOCK:
        if _SESSION is None:
            _SESSION=Session()
        session=_SESSION
    display(session.panel)
    session.start(False,'automatic')
    return session
