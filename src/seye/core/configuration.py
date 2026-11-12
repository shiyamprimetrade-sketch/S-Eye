"""Strict versioned local configuration; pure migration never rewrites user files."""
from pathlib import Path
from seye.core.storage import read_json
from seye.integration.service import Permissions


def load_config(path):
    data = read_json(path, max_bytes=64 * 1024)
    if not isinstance(data, dict):
        raise ValueError('Configuration object required')
    source_version = data.get('schema_version')
    if type(source_version) is not int:
        raise ValueError('Configuration schema version must be an integer')
    if source_version == 0:
        if set(data) - {'schema_version', 'allowed_directory', 'allow_write', 'allow_memory'}:
            raise ValueError('Unknown version-0 configuration fields')
        for field in ('allow_write', 'allow_memory'):
            if field in data and type(data[field]) is not bool:
                raise ValueError('Configuration capabilities must be booleans')
        directory = data.get('allowed_directory')
        data = {'schema_version': 1, 'read_roots': [directory],
                'write_roots': [directory] if data.get('allow_write', False) else [],
                'memory': data.get('allow_memory', False)}
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('Unsupported configuration version')
    if set(data) - {'schema_version', 'read_roots', 'write_roots', 'memory', 'training', 'video', 'timeout'}:
        raise ValueError('Unknown configuration fields')
    roots = {}
    for field in ('read_roots', 'write_roots'):
        values = data.get(field, [])
        if not isinstance(values, list) or len(values) > 32 or any(not isinstance(v, str) or not Path(v).expanduser().is_absolute() for v in values):
            raise ValueError('Configuration roots must be absolute path lists')
        roots[field] = tuple(str(Path(v).expanduser().resolve()) for v in values)
    flags = {}
    for field in ('memory', 'training', 'video'):
        flags[field] = data.get(field, False)
        if type(flags[field]) is not bool:
            raise ValueError('Configuration capabilities must be booleans')
    timeout = data.get('timeout', 30)
    if type(timeout) not in (int, float) or not 0 < timeout <= 120:
        raise ValueError('Configuration timeout must be in (0,120]')
    return {'schema_version': 1, 'source_version': source_version,
            'permissions': Permissions(roots['read_roots'], roots['write_roots'], **flags), 'timeout': timeout}
