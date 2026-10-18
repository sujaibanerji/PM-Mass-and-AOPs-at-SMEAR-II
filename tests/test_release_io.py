import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from release_io import prepare_release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dest = self.root / 'prepared release'
        self.local = {}
        self.config = self.root / 'release.json'
        self.spec = dict(release_id='test', archives={})
        payloads = {'codes': {'package_checks.py': 'import sys\n'},
                    'data': {'observation.txt': 'original'},
                    'additional_figures': {'manifest.json': '{"files": [], "figures": []}'}}
        for key, entries in payloads.items():
            p = self.root / (key + '.zip')
            with zipfile.ZipFile(p, 'w') as z:
                for name, data in entries.items():
                    z.writestr(name, data)
            self.local[key] = p
            self.describe(key)
        self.save()

    def describe(self, key):
        p = self.local[key]
        self.spec['archives'][key] = dict(filename=p.name, bytes=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest(), url=None)

    def save(self):
        self.config.write_text(json.dumps(self.spec))

    def test_corrupted_archive_leaves_no_partial_destination(self):
        self.local['data'].write_bytes(b'corrupt')
        with self.assertRaises(ValueError):
            prepare_release(self.config, self.dest, self.local)
        self.assertFalse(self.dest.exists())
        self.assertEqual(self.local['data'].read_bytes(), b'corrupt')

    def test_failed_download_leaves_no_partial_destination(self):
        for a in self.spec['archives'].values():
            a['url'] = 'https://example.invalid/' + a['filename']
        self.save()
        with patch('release_io.urlopen', side_effect=OSError('network failed')):
            with self.assertRaises(OSError):
                prepare_release(self.config, self.dest)
        self.assertFalse(self.dest.exists())

    def test_zip_path_escape_is_rejected(self):
        with zipfile.ZipFile(self.local['data'], 'w') as z:
            z.writestr('../escaped.txt', 'bad')
        self.describe('data'); self.save()
        with self.assertRaises(ValueError):
            prepare_release(self.config, self.dest, self.local)
        self.assertFalse((self.root / 'escaped.txt').exists())
        self.assertFalse(self.dest.exists())

    def test_missing_urls_fail_clearly(self):
        with self.assertRaisesRegex(ValueError, 'HTTPS URLs'):
            prepare_release(self.config, self.dest)

    def test_zip_symlink_is_rejected(self):
        with zipfile.ZipFile(self.local['data'], 'w') as z:
            entry = zipfile.ZipInfo('link')
            entry.create_system = 3
            entry.external_attr = 0o120777 << 16
            z.writestr(entry, '/etc/passwd')
        self.describe('data'); self.save()
        with self.assertRaisesRegex(ValueError, 'links'):
            prepare_release(self.config, self.dest, self.local)
        self.assertFalse(self.dest.exists())

    def test_unrelated_destination_is_preserved(self):
        self.dest.mkdir()
        (self.dest / 'precious.txt').write_text('keep')
        with self.assertRaises(FileExistsError):
            prepare_release(self.config, self.dest, self.local)
        self.assertEqual((self.dest / 'precious.txt').read_text(), 'keep')

    def test_same_validated_release_reused_and_tampering_detected(self):
        first = prepare_release(self.config, self.dest, self.local)
        second = prepare_release(self.config, self.dest, self.local)
        self.assertEqual(first['data'], second['data'])
        (Path(first['data']) / 'observation.txt').write_text('changed')
        with self.assertRaises(ValueError):
            prepare_release(self.config, self.dest, self.local)
