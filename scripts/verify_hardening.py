#!/usr/bin/env python3
"""Run installed-dependency and hardening checks with a machine-readable receipt."""
import argparse
from importlib.metadata import requires, version
from pathlib import Path
import sys
import tomllib
import unittest

from seye.core.storage import atomic_json

ROOT = Path(__file__).resolve().parents[1]


def verify_dependencies():
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']
    pins = (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines()
    distribution = project['name']
    installed = [entry.replace(' ', '') for entry in requires(distribution) or []]
    if sorted(pins) != sorted(project['dependencies']) or sorted(pins) != sorted(installed):
        raise ValueError('Source requirements and installed wheel dependencies differ')
    for pin in pins:
        name, expected = pin.split('==', 1)
        if version(name) != expected:
            raise ValueError(f'Installed {name} differs from the declared pin')
    if version(distribution) != project['version']:
        raise ValueError('Installed distribution version differs from the declared version')
    return {'distribution': distribution, 'version': version(distribution), 'dependency_pins': pins}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    dependencies = verify_dependencies()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_stage181_190.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    atomic_json(args.output, {
        'schema_version': 1,
        'scope': 'local generated regression controls and installed dependency metadata',
        'dependencies': dependencies,
        'tests_run': result.testsRun,
        'skipped': [{'test': test.id(), 'reason': reason} for test, reason in result.skipped],
        'failures': len(result.failures),
        'errors': len(result.errors),
        'passed': result.wasSuccessful() and result.testsRun == 8,
    })
    sys.exit(0 if result.wasSuccessful() and result.testsRun == 8 else 1)
