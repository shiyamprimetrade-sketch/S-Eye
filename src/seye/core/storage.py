"""Canonical checksums and exclusive atomic JSON checkpoints."""
import hashlib
import json
import os
from pathlib import Path
import tempfile


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def checksum(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path, max_bytes=16 * 1024 * 1024):
    with Path(path).open('rb') as stream:
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError('JSON exceeds byte limit')
    return json.loads(raw, parse_constant=lambda text: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def atomic_json(path, value, overwrite=False):
    path = Path(path)
    encoded = canonical(value) + b'\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix='.seye-', suffix='.tmp')
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(name, path)
        else:
            os.link(name, path)  # Exclusive atomic publication; cannot overwrite a raced target.
    finally:
        Path(name).unlink(missing_ok=True)
    return path
