"""Memory calls must pass authorization before opening the image decoder."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from seye.integration.service import Permissions, execute


class LegacyMemoryPermissionTests(unittest.TestCase):
    def test_memory_denials_precede_image_analysis(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            'seye.integration.service.analyze'
        ) as analyze:
            root = Path(directory)
            request = {'schema_version': 1, 'request_id': 'memory-gates', 'action': 'remember',
                       'image': str(root / 'image.png'), 'memory': str(root / 'memory.sqlite3')}
            for permissions in (Permissions(read_roots=(root,), write_roots=(root,)),
                                Permissions(read_roots=(root,), memory=True)):
                with self.subTest(permissions=permissions), self.assertRaises(PermissionError):
                    execute(request, permissions)
            analyze.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])


class CheckpointEvidenceTests(unittest.TestCase):
    def test_release_audit_rejects_checkpoint_from_different_source(self):
        from seye.core.storage import atomic_json
        import subprocess
        import sys

        audit = Path(__file__).resolve().parents[1] / 'scripts/release_audit.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / 'stale.json'
            output = root / 'readiness.json'
            atomic_json(report, {'schema_version': 1, 'source_sha256': {}})
            result = subprocess.run([sys.executable, str(audit), '--checkpoint', str(report),
                                     '--output', str(output)], capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('does not match current source', result.stderr)
            self.assertFalse(output.exists())
