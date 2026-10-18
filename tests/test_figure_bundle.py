import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
import zipfile

from tools.package_figures import build_bundle


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        figures = []
        for group, data in [('a', b'first'), ('b', b'second')]:
            p = self.root / group / 'figure_1.png'
            p.parent.mkdir()
            p.write_bytes(data)
            figures.append(dict(id=group, canonical_source=f'project:{group}/figure_1.png',
                                sha256=hashlib.sha256(data).hexdigest(), formats=[],
                                regeneration='archived_image', title=group, provenance=[]))
        self.inventory = self.root / 'inventory.json'
        self.inventory.write_text(json.dumps(dict(figures=figures, unresolved=[])))
        self.output = self.root / 'additional.zip'

    def test_two_groups_with_same_filename_both_survive(self):
        report = build_bundle(self.inventory, self.root, self.output)
        self.assertEqual(report['figure_count'], 2)
        with zipfile.ZipFile(self.output) as z:
            self.assertIn('figures/a/figure_1.png', z.namelist())
            self.assertIn('figures/b/figure_1.png', z.namelist())

    def test_packaging_command_runs_from_repository_root(self):
        script = Path(__file__).resolve().parents[1] / 'tools/package_figures.py'
        result = subprocess.run([sys.executable, script, '--inventory', self.inventory,
            '--source-root', self.root, '--output', self.output], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['figure_count'], 2)

    def test_bundle_bytes_match_sources(self):
        build_bundle(self.inventory, self.root, self.output)
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(z.read('figures/a/figure_1.png'), b'first')
            self.assertEqual(z.read('figures/b/figure_1.png'), b'second')

    def test_public_manifest_contains_no_absolute_local_paths(self):
        build_bundle(self.inventory, self.root, self.output)
        with zipfile.ZipFile(self.output) as z:
            manifest = z.read('manifest.json').decode()
            self.assertNotIn(str(self.root), manifest)
            self.assertEqual(len(json.loads(manifest)['files']), 2)
