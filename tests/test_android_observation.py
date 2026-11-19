import hashlib
from pathlib import Path
import tempfile
import unittest

from seye.core.storage import atomic_json
from seye.integration.contracts import validate_request
from seye.integration.service import Permissions, handle


class AndroidObservationTests(unittest.TestCase):
    def test_source_check_and_grants(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image, report = root / 'image.png', root / 'report.json'
            image.write_bytes(b'bytes used by this test')
            payload = {'format': 'seye-android-observation-v1', 'schema_version': 1,
                       'app_version': '0.3.0-preview', 'source_kind': 'document',
                       'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                       'source_bytes': len(image.read_bytes()), 'analyzed_size': [128, 64],
                       'label': 'Triangle', 'accepted': True}
            atomic_json(report, payload)
            request = {'schema_version': 1, 'request_id': 'android-test', 'action': 'android_observation',
                       'report': str(report), 'image': str(image)}
            validate_request(request, strict=True)
            self.assertFalse(handle(request, Permissions())['success'])
            permissions = Permissions(read_roots=(root,))
            result = handle(request, permissions)['result']
            self.assertTrue(result['source_bytes_match'])
            self.assertFalse(result['classification_verified'])
            image.write_bytes(b'different input')
            self.assertFalse(handle(request, permissions)['success'])
            request.pop('image')
            self.assertIsNone(handle(request, permissions)['result']['source_bytes_match'])
            atomic_json(report, {**payload, 'accepted': False}, overwrite=True)
            self.assertFalse(handle(request, permissions)['success'])
