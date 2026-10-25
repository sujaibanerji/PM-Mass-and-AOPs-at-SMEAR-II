"""Local UI-contract tests; fake widgets/runner, no network or cloud execution."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
PROMPT=('Click the Binder link once, then wait. Everything will start automatically. '
        'Keep the tab open; do not click Run, change settings, or refresh the page. '
        'The figures and download links will appear when processing finishes.')


class Widget:
    def __init__(self,*args,**kwargs):
        self.value=kwargs.get('value',''); self.disabled=kwargs.get('disabled',False)
        self.description=kwargs.get('description','')
        self.layout=kwargs.get('layout',types.SimpleNamespace(display=''))
        self.children=args[0] if args else ()
        self.callbacks=[]; self.messages=[]
    def on_click(self,callback): self.callbacks.append(callback)
    def click(self):
        # Also simulate an already-queued click arriving after disablement.
        for callback in self.callbacks: callback(self)
    def append_stdout(self,text): self.messages.append(text)
    def append_stderr(self,text): self.messages.append(text)
    def __enter__(self): return self
    def __exit__(self,*args): return False


class AutoStartTests(unittest.TestCase):
    def setUp(self):
        self.displayed=[]; self.calls=[]; self.pending=[]; self.failure=False
        self.result=ROOT/'outputs/test result'
        widgets=types.ModuleType('ipywidgets')
        for name in ('Checkbox','Button','Output','HTML','VBox','HBox'):
            setattr(widgets,name,Widget)
        widgets.Layout=lambda **kwargs:types.SimpleNamespace(display='',**kwargs) if 'display' not in kwargs else types.SimpleNamespace(**kwargs)
        display=types.ModuleType('IPython.display')
        display.display=lambda *items:self.displayed.extend(items)
        display.HTML=lambda value:value
        display.FileLink=lambda value:value
        launcher=types.ModuleType('launcher'); launcher.HERE=ROOT
        def run(**kwargs):
            self.calls.append(kwargs['historical'])
            kwargs.get('progress',lambda *_:None)('Progress: test step')
            if self.failure: raise RuntimeError('fixture download failure')
            return self.result
        launcher.run=run
        io=types.ModuleType('release_io')
        io.configuration=lambda:dict(release_id='binder-20261019-dust-evidence')
        self.modules=patch.dict(sys.modules,{'ipywidgets':widgets,'IPython.display':display,
                                             'launcher':launcher,'release_io':io})
        self.modules.start(); self.addCleanup(self.modules.stop)
        spec=importlib.util.spec_from_file_location('ui_under_test',ROOT/'one_click.py')
        self.ui=importlib.util.module_from_spec(spec); spec.loader.exec_module(self.ui)
        pending=self.pending
        class QueuedThread:
            def __init__(self,*,target,daemon): self.target=target
            def start(self): pending.append(self.target)
        self.worker=patch.object(self.ui,'Thread',QueuedThread,create=True)
        self.worker.start(); self.addCleanup(self.worker.stop)

    def finish(self):
        self.assertEqual(len(self.pending),1)
        self.pending.pop(0)()

    def test_show_automatically_runs_default_once_and_displays_progress_links(self):
        view=self.ui.show()
        self.finish()
        self.assertEqual(self.calls,[False])
        self.assertIn('Progress: test step',''.join(view.output.messages))
        self.assertIn('results.zip',view.links.value)
        self.assertIn('figure_1.png',view.links.value)
        self.assertIn('figure_8.png',view.links.value)
        self.assertIn('test%20result',view.links.value)
        self.assertIn('finished',view.status.value.lower())

    def test_rerender_during_and_after_success_never_schedules_duplicate(self):
        first=self.ui.show(); second=self.ui.show()
        self.assertIs(first,second)
        self.finish()
        self.assertIs(first,self.ui.show())
        self.assertEqual(self.calls,[False]); self.assertEqual(self.pending,[])

    def test_instruction_is_visible_without_any_user_action(self):
        self.ui.show()
        self.assertIn(PROMPT,' '.join(str(x) for x in self.displayed))

    def test_historical_controls_hidden_disabled_until_success(self):
        view=self.ui.show()
        self.assertEqual(view.advanced.layout.display,'none')
        self.assertTrue(view.option.disabled); self.assertTrue(view.button.disabled)
        self.assertEqual(view.retry.layout.display,'none')
        view.option.value=True; view.button.click()
        self.finish()
        self.assertEqual(self.calls,[False])
        self.assertNotEqual(view.advanced.layout.display,'none')
        self.assertFalse(view.button.disabled)

    def test_failure_visible_no_rerender_retry_and_explicit_retry_only(self):
        self.failure=True
        view=self.ui.show(); self.finish()
        self.assertIn('fixture download failure',''.join(view.output.messages))
        self.assertIn('failed',view.status.value.lower())
        self.assertNotEqual(view.retry.layout.display,'none')
        self.assertEqual(view.advanced.layout.display,'none')
        self.ui.show(); self.assertEqual(self.pending,[])
        self.failure=False; view.retry.click(); view.retry.click()
        self.finish()
        self.assertEqual(self.calls,[False,False])
        self.assertEqual(view.retry.layout.display,'none')

    def test_historical_run_requires_explicit_click_after_success(self):
        view=self.ui.show(); self.finish()
        view.option.value=True
        self.ui.show(); self.assertEqual(self.calls,[False])
        view.button.click(); view.button.click(); self.finish()
        self.assertEqual(self.calls,[False,True])

    def test_success_does_not_allow_stale_retry_click(self):
        view=self.ui.show(); self.finish()
        view.retry.click()
        self.assertEqual(self.pending,[]); self.assertEqual(self.calls,[False])

    def test_explicit_module_reload_preserves_completed_session(self):
        view=self.ui.show(); self.finish()
        queued_thread=self.ui.Thread
        self.ui.__spec__.loader.exec_module(self.ui)
        with patch.object(self.ui,'Thread',queued_thread):
            self.assertIs(view,self.ui.show())
        self.assertEqual(self.pending,[]); self.assertEqual(self.calls,[False])


if __name__=='__main__': unittest.main(verbosity=2)
