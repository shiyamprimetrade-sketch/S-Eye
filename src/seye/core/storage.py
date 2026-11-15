"""Canonical checksums and exclusive atomic JSON checkpoints."""
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def checksum(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def decode_json(raw,max_bytes=16*1024*1024,max_depth=64):
    if type(max_bytes) is not int or not 1<=max_bytes<=64*1024*1024 or type(max_depth) is not int or not 1<=max_depth<=64:
        raise ValueError('Bounded JSON byte/depth limits required')
    if not isinstance(raw,bytes) or len(raw)>max_bytes:raise ValueError('JSON exceeds byte limit')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate JSON field')
            result[key]=value
        return result
    try:
        value=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=unique,
                         parse_constant=lambda text:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except RecursionError as error:raise ValueError('JSON parser nesting exceeded') from error
    nodes=0
    def validate(item,depth):
        nonlocal nodes
        nodes+=1
        if nodes>1000000 or depth>max_depth:raise ValueError('JSON depth/node budget exceeded')
        if type(item) is dict:
            for key,child in item.items():validate(key,depth+1);validate(child,depth+1)
        elif type(item) is list:
            for child in item:validate(child,depth+1)
        elif type(item) is str:item.encode('utf-8')
        elif type(item) is float and not math.isfinite(item):raise ValueError('Nonfinite JSON number')
    validate(value,0)
    return value


def read_json(path,max_bytes=16*1024*1024):
    if type(max_bytes) is not int or not 1<=max_bytes<=64*1024*1024:raise ValueError('Bounded positive JSON byte limit required')
    path=Path(path)
    if path.exists() and not path.is_file():raise ValueError('JSON input must be a regular file')
    with path.open('rb') as stream:raw=stream.read(max_bytes+1)
    return decode_json(raw,max_bytes)


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
