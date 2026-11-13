"""Make historical print-only experiments into executable regression gates."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from generalization import ROOT


class LegacyRegressionTests(unittest.TestCase):
    def test_historical_geometry(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for name in ('stress_test.py', 'geometry_v2_runner.py', 'geometry_challenge.py',
                         'uncertainty_test.py', 'borderline_test.py'):
                shutil.copy2(ROOT / name, work / name)

            def execute(name):
                result = subprocess.run([sys.executable, name], cwd=work,
                                        capture_output=True, text=True, timeout=120)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout

            stress = execute('stress_test.py')
            self.assertEqual(stress.count(' PASS'), 20)
            self.assertNotIn('FAIL', stress)
            execute('geometry_challenge.py')
            geometry = execute('geometry_v2_runner.py')
            labels = re.findall(r'^Object \d+: ([^,]+),', geometry, re.M)
            self.assertEqual(labels, ['Circle-like', 'Square', 'Square', 'Rectangle', 'Triangle', 'Triangle'])
            self.assertIn('Tests: 9/9', execute('uncertainty_test.py'))
            # Preserve and expose this known weakness; it is not a passing accuracy claim.
            self.assertIn('Correct: 4/8', execute('borderline_test.py'))
