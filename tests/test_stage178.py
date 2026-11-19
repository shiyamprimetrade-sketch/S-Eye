import unittest
from pathlib import Path
import tomllib
from seye.local.cli import parser
from seye.local.doctor import doctor
from seye import __version__

class InstallationDoctorTests(unittest.TestCase):
    def test_development_version_cli_surface_and_metadata_without_side_effect_claim(self):
        metadata = tomllib.loads((Path(__file__).resolve().parents[1] / 'pyproject.toml').read_text(encoding='utf-8'))
        self.assertEqual(__version__, metadata['project']['version'])
        self.assertRegex(__version__, r'^0\.1\.0\.dev[0-9]+$')
        args=parser().parse_args(['doctor']);self.assertEqual(args.command,'doctor')
        report=doctor();self.assertEqual(report['code_version'],__version__);self.assertIsNone(report['self_test'])
        self.assertFalse(report['hardware_validation']);self.assertFalse(report['v1_release'])

    def test_generated_opt_in_selftest_is_bounded_and_labelled(self):
        report=doctor(True)
        self.assertEqual(report['self_test']['generated_images'],1)
        self.assertTrue(report['self_test']['offline_report_created'])
        self.assertFalse(report['hardware_validation'])
