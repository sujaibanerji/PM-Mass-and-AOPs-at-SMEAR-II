import hashlib
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile

from release_io import check_archive, safe_extract, safe_parts


class LauncherTests(unittest.TestCase):
    def test_good_flat_name(self):
        self.assertEqual(safe_parts('observations/a.csv'), ('observations', 'a.csv'))

    def test_reject_dangerous_names(self):
        for name in ['../escape', '/absolute', 'C:/file', 'a/../../b', 'a\\b', 'a//b', './file', 'a:b', 'a./x', 'CON/file']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_parts(name)

    def test_hash_or_size_mismatch(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as d:
            p=Path(d)/'archive.zip'
            p.write_bytes(b'not a zip')
            for record in [dict(bytes=1,sha256='0'*64), dict(bytes=p.stat().st_size,sha256='0'*64)]:
                with self.assertRaises(ValueError):
                    check_archive(p,record)

    def test_safe_extract_and_crc(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as d:
            root=Path(d); p=root/'ok.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('one/file.txt','example')
            safe_extract(p,root/'out')
            self.assertEqual((root/'out/one/file.txt').read_text(),'example')
            with self.assertRaises(FileExistsError):
                safe_extract(p,root/'out')

    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as d:
            root=Path(d); p=root/'bad.zip'
            info=zipfile.ZipInfo('link'); info.create_system=3
            info.external_attr=(stat.S_IFLNK|0o777)<<16
            with zipfile.ZipFile(p,'w') as z:
                z.writestr(info,'outside')
            with self.assertRaises(ValueError):
                safe_extract(p,root/'out')

    def test_reject_case_collision_before_extract(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as d:
            root=Path(d); p=root/'bad.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('File.txt','a'); z.writestr('file.txt','b')
            with self.assertRaises(ValueError):
                safe_extract(p,root/'out')
            self.assertFalse((root/'out').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
