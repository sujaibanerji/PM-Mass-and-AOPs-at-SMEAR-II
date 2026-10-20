"""The slow scientific calculation is replaced at its boundary, not the UI/state logic."""
import hashlib
from contextvars import ContextVar
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import zipfile

from reviewer import build_gallery, export_results


class OneClickTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('one_click'), 'One-click launcher is missing')
        from one_click import Dashboard
        self.Dashboard = Dashboard
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def app(self, runner):
        return self.Dashboard(config=self.root / 'release.json', runtime=self.root / 'runtime',
                              outputs=self.root / 'outputs', runner=runner)

    def wait_finished(self, app):
        deadline = time.monotonic() + 10
        while app.running and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertFalse(app.running, 'Button calculation did not finish')

    def fixture_run(self, prepared, output, *, confirmed):
        self.assertIs(confirmed, True)
        output.mkdir(parents=True, exist_ok=False)
        analysis = output / 'analysis'; analysis.mkdir()
        (analysis / 'table.csv').write_text('value\n42\n')
        image = output / 'fixture.png'; image.write_bytes(b'fixture')
        manifest = dict(production=True, expected_ids=['main_1'], figures=[dict(
            id='main_1', title='Test', group='main', scope='fixture',
            estimate_origin='fixed_artwork', regeneration='registered',
            path=str(image), sha256=hashlib.sha256(b'fixture').hexdigest(), formats=[])])
        build_gallery(manifest, output / 'gallery')
        export_results(manifest, output / 'all_figures.zip')
        return manifest

    def test_opening_page_does_not_start_analysis(self):
        def forbidden(*args, **kwargs):
            self.fail('Opening the page must wait for the user click')
        app = self.app(forbidden)
        self.assertFalse(app.running)
        self.assertFalse(app.button.disabled)
        self.assertFalse((self.root / 'outputs').exists())
        self.assertEqual(app.downloads.value, '')

    def test_one_click_runs_once_and_publishes_complete_downloads(self):
        started, release = threading.Event(), threading.Event()
        def blocked(prepared, output, *, confirmed):
            started.set()
            if not release.wait(5):
                raise TimeoutError('Test runner was not released')
            return self.fixture_run(prepared, output, confirmed=confirmed)
        app = self.app(blocked)
        with patch('one_click.prepare_release', return_value={'verified':True}):
            app.button.click()
            self.assertTrue(started.wait(3))
            self.assertTrue(app.button.disabled)
            app.button.click()  # queued/double click must not create a second job
            release.set()
            self.wait_finished(app)
        directories = list((self.root / 'outputs').glob('production_*'))
        self.assertEqual(len(directories), 1)
        self.assertIn('all_figures.zip', app.downloads.value)
        self.assertIn('analysis_tables_and_logs.zip', app.downloads.value)
        self.assertIn('Complete', app.status.value)
        with zipfile.ZipFile(directories[0] / 'analysis_tables_and_logs.zip') as z:
            self.assertEqual(z.read('analysis/table.csv'), b'value\n42\n')
            self.assertNotIn('all_figures.zip', z.namelist())
        self.assertEqual(json.loads((directories[0]/'one_click_run.json').read_text())['status'], 'completed')

    def test_failure_keeps_logs_and_allows_retry_without_success_links(self):
        def fail(prepared, output, *, confirmed):
            output.mkdir(parents=True, exist_ok=False)
            (output/'production.log').write_text('diagnostic evidence')
            raise RuntimeError('Calculation failed <check log>')
        app = self.app(fail)
        with patch('one_click.prepare_release', return_value={'verified':True}):
            app.button.click()
            self.wait_finished(app)
        self.assertFalse(app.button.disabled)
        self.assertIn('failed', app.status.value.lower())
        self.assertNotIn('<check log>', app.status.value)
        self.assertEqual(app.downloads.value, '')
        self.assertEqual(len(list((self.root/'outputs').glob('production_*/production.log'))), 1)

    def test_background_calculation_keeps_kernel_request_context(self):
        parent = ContextVar('shell_parent')
        parent.set('button-request')
        def contextual(prepared, output, *, confirmed):
            self.assertEqual(parent.get(), 'button-request')
            return self.fixture_run(prepared, output, confirmed=confirmed)
        app = self.app(contextual)
        with patch('one_click.prepare_release', return_value={'verified':True}):
            app.button.click()
            self.wait_finished(app)
        self.assertIn('Complete', app.status.value)
