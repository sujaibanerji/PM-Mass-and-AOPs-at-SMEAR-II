import hashlib
import contextlib
import io
import json
from pathlib import Path
import tempfile
import sys
import unittest
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
