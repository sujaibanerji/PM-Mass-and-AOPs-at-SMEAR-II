import hashlib
import ast
import contextlib
from contextvars import ContextVar
import io
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import sys
import unittest
import warnings
from unittest.mock import patch
import zipfile

from reviewer import build_gallery, export_results, estimate_origin, run_full, run_live


class ReviewerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        figures = []
        for name, data in [('main', b'a'), ('history', b'b')]:
            p = self.root / name / 'figure_1.png'
            p.parent.mkdir(); p.write_bytes(data)
            figures.append(dict(id=name, path=str(p), sha256=hashlib.sha256(data).hexdigest(),
                title='<script>alert(1)</script>', group=name, scope='scope',
                estimate_origin='saved_reference' if name == 'main' else 'archived_image',
                regeneration='registered' if name == 'main' else 'archived_image', formats=[]))
        self.manifest = dict(figures=figures, expected_ids=['main', 'history'])

    def test_same_named_images_survive_gallery_and_export(self):
        gallery = build_gallery(self.manifest, self.root / 'gallery')
        exported = export_results(self.manifest, self.root / 'results.zip')
        self.assertTrue(gallery.is_file())
        with zipfile.ZipFile(exported) as z:
            self.assertEqual(z.read('figures/main/figure_1.png'), b'a')
            self.assertEqual(z.read('figures/history/figure_1.png'), b'b')
            public = json.loads(z.read('manifest.json'))
            self.assertNotIn(str(self.root), json.dumps(public))

    def test_missing_expected_image_stops_completion(self):
        Path(self.manifest['figures'][0]['path']).unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            build_gallery(self.manifest, self.root / 'gallery')

    def test_missing_inventory_entry_stops_completion(self):
        self.manifest['figures'].pop()
        with self.assertRaises(ValueError):
            build_gallery(self.manifest, self.root / 'gallery')

    def test_origins_preserve_saved_and_archived_status(self):
        self.assertEqual(estimate_origin('main_7', 'registered', False), 'saved_reference')
        self.assertEqual(estimate_origin('historical', 'archived_image', True), 'archived_image')
        self.assertEqual(estimate_origin('main_1', 'registered', True), 'fixed_artwork')

    def test_captions_are_escaped(self):
        page = build_gallery(self.manifest, self.root / 'gallery').read_text(encoding='utf-8')
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertIn('&lt;script&gt;', page)

    def test_export_cannot_include_its_own_zip(self):
        build_gallery(self.manifest, self.root / 'gallery')
        with self.assertRaises(ValueError):
            export_results(self.manifest, self.root / 'gallery' / 'all.zip')

    def test_full_run_requires_explicit_opt_in(self):
        with patch('reviewer.subprocess.Popen') as launch:
            with self.assertRaises(ValueError):
                run_full({}, self.root / 'production', confirmed=False)
        launch.assert_not_called()
        self.assertFalse((self.root / 'production').exists())

    def test_silent_launcher_exposes_live_job_log_progress(self):
        jobs = self.root / 'analysis'; jobs.mkdir()
        command = [sys.executable, '-c',
            'import pathlib,sys; pathlib.Path(sys.argv[1]).write_text("[1/25] recalculated.\\n")',
            str(jobs / 'job.log')]
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            run_live(command, self.root / 'launch.log', progress_directory=jobs)
        self.assertIn('[1/25] recalculated.', capture.getvalue())

    def test_job_log_watcher_keeps_kernel_request_context(self):
        parent = ContextVar('shell_parent')
        parent.set('button-request')
        class ContextOutput(io.StringIO):
            def write(self, text):
                if text:
                    parent.get()  # Real widget comms require this request context.
                return super().write(text)
        jobs = self.root / 'analysis'; jobs.mkdir()
        command = [sys.executable, '-c',
                   'import pathlib,sys; pathlib.Path(sys.argv[1]).write_text("watcher progress")',
                   str(jobs / 'job.log')]
        capture = ContextOutput()
        with contextlib.redirect_stdout(capture):
            run_live(command, self.root/'launch.log', progress_directory=jobs)
        self.assertIn('watcher progress', capture.getvalue())

    def test_notebook_gallery_uses_static_srcdoc_with_authenticated_file_base(self):
        from reviewer import notebook_gallery
        gallery = build_gallery(self.manifest, self.root / 'gallery')
        class Frames(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag == 'iframe':
                    self.frame = dict(attrs)
        parser = Frames()
        parser.feed(notebook_gallery(gallery, '/user/reviewer/files/outputs/run/gallery/'))
        frame = parser.frame
        self.assertNotIn('src', frame)
        self.assertEqual(set(frame['sandbox'].split()), {'allow-same-origin', 'allow-downloads'})
        self.assertIn('<base href="/user/reviewer/files/outputs/run/gallery/">', frame['srcdoc'])
        self.assertIn('figures/main/figure_1.png', frame['srcdoc'])
        self.assertNotIn('data:image', frame['srcdoc'])
        self.assertNotIn('<script>alert(1)</script>', frame['srcdoc'])
        with self.assertRaises(ValueError):
            notebook_gallery(gallery, 'https://another.example/')

    def test_production_introduction_describes_recalculated_and_archived_scope(self):
        self.manifest['production'] = True
        page = build_gallery(self.manifest, self.root / 'gallery').read_text(encoding='utf-8')
        self.assertIn('Current production estimates have been recalculated.', page)
        self.assertIn('Figure 1 is fixed artwork; historical figures remain archived.', page)
        self.assertNotIn('Saved-reference intervals have not been recalculated.', page)

    def test_portable_export_links_resolve_without_external_zip(self):
        gallery = build_gallery(self.manifest, self.root / 'gallery')
        live = gallery.read_text(encoding='utf-8')
        self.assertIn('../all_figures.zip', live)
        archive = export_results(self.manifest, self.root / 'all_figures.zip')
        class Links(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    self.links.append(dict(attrs)['href'])
        parser = Links(); parser.links = []
        with zipfile.ZipFile(archive) as z:
            parser.feed(z.read('index.html').decode())
            for link in parser.links:
                self.assertIn(link, z.namelist(), f'Unresolved portable download link: {link}')
        self.assertEqual(gallery.read_text(encoding='utf-8'), live)

    def test_both_notebook_gallery_displays_emit_no_iframe_advisory(self):
        try:
            from IPython.display import HTML, display
        except ImportError:
            self.skipTest('Requires the notebook runtime; checked in Linux acceptance')
        from reviewer import notebook_gallery
        gallery = build_gallery(self.manifest, self.root / 'gallery')
        notebook = json.loads((Path(__file__).resolve().parents[1] / 'Start_here.ipynb').read_text())
        calls = []
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                tree = ast.parse(''.join(cell['source']))
                calls.extend(node for node in ast.walk(tree) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id == 'display'
                    and any(isinstance(child, ast.Name) and child.id == 'notebook_gallery'
                            for child in ast.walk(node)))
        self.assertEqual(len(calls), 2)
        scope = dict(HTML=HTML, display=display, notebook_gallery=notebook_gallery,
                     gallery=gallery, full_output=self.root,
                     file_url=lambda path: '/user/reviewer/files/outputs/gallery')
        with warnings.catch_warnings(record=True) as emitted, contextlib.redirect_stdout(io.StringIO()):
            warnings.simplefilter('always')
            for call in calls:
                eval(compile(ast.Expression(call), '<notebook-gallery>', 'eval'), scope)
        self.assertFalse([str(w.message) for w in emitted if 'IPython.display.IFrame' in str(w.message)])
