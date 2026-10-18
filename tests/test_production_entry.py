import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import venv


@unittest.skipUnless(os.name == 'posix', 'Linux symlinked virtual environment regression')
class ProductionEntryTests(unittest.TestCase):
    def test_original_launcher_children_keep_virtual_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            venv.EnvBuilder(symlinks=True).create(root / 'env')
            python = root / 'env/bin/python'
            site = Path(subprocess.check_output([python, '-c',
                'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip())
            (site / 'only_in_this_environment.py').write_text('VALUE = 731\n')
            codes = root / 'codes'; codes.mkdir()
            (codes / 'run_all.py').write_text('''import subprocess,sys
from pathlib import Path
def resolve_executable(value): return str(Path(value).resolve())
def main(argv):
    subprocess.run([resolve_executable(sys.executable), '-c', 'from only_in_this_environment import VALUE; print(VALUE)'], check=True)
''')
            wrapper = Path(__file__).resolve().parents[1] / 'production_entry.py'
            result = subprocess.run([python, wrapper, '--codes-dir', codes],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('731', result.stdout)
