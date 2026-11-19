"""Validate a bounded Android shape observation and optionally check source bytes."""
import hashlib
import re

from seye.core.files import read_bounded
from seye.core.storage import read_json

MAX_IMAGE_BYTES = 12 * 1024 * 1024
_FIELDS = {'format', 'schema_version', 'app_version', 'source_kind', 'sha256',
           'source_bytes', 'analyzed_size', 'label', 'accepted'}
_LABELS = ('Circle', 'Triangle', 'Quadrilateral', 'Unknown')


def load_observation(report, image=None):
    row = read_json(report, max_bytes=4096)
    if (not isinstance(row, dict) or row.keys() != _FIELDS
            or row['format'] != 'seye-android-observation-v1'
            or type(row['schema_version']) is not int or row['schema_version'] != 1):
        raise ValueError('Expected a schema-1 S-Eye Android observation')
    if not isinstance(row['app_version'], str) or not re.fullmatch(
            r'\d{1,3}\.\d{1,3}\.\d{1,3}(?:-preview)?', row['app_version']):
        raise ValueError('Invalid Android app version')
    if row['source_kind'] not in ('document', 'sample', 'camera_thumbnail'):
        raise ValueError('Unsupported source kind')
    if not isinstance(row['sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', row['sha256']):
        raise ValueError('Invalid source digest')
    if type(row['source_bytes']) is not int or not 1 <= row['source_bytes'] <= MAX_IMAGE_BYTES:
        raise ValueError('Invalid source byte count')
    size = row['analyzed_size']
    if not isinstance(size, list) or len(size) != 2 or any(type(n) is not int or not 1 <= n <= 768 for n in size):
        raise ValueError('Invalid analyzed dimensions')
    if (row['label'] not in _LABELS or type(row['accepted']) is not bool
            or row['accepted'] != (row['label'] != 'Unknown')
            or (row['accepted'] and min(size) < 16)):
        raise ValueError('Inconsistent shape decision')
    if image is not None:
        data = read_bounded(image, MAX_IMAGE_BYTES)
        if len(data) != row['source_bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Supplied image bytes do not match the observation')
    return {'observation': row, 'source_bytes_match': True if image is not None else None,
            'classification_verified': False, 'scope': 'Caller-supplied geometry observation'}
