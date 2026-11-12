"""Offline observation memory with transactions, content identity and verified transfer.

Legacy JSONL import preserves records verbatim; absent descriptors stay absent.
Retrieval is an exact linear descriptor scan, not a large-scale ANN index.
"""
import json
import os
from pathlib import Path
import sqlite3
from seye.core.storage import canonical, checksum, read_json, atomic_json
from seye.recognition.features import FEATURE_VERSION, distance

APPLICATION_ID = 1397053765


def validate_record(record):
    if not isinstance(record, dict) or type(record.get('schema_version')) is not int or record.get('schema_version') != 1:
        raise ValueError('Memory observation schema required')
    if record.get('features') is not None:
        if not isinstance(record['features'], list) or record.get('feature_version') != FEATURE_VERSION or len(record['features']) > 4096:
            raise ValueError('Incompatible memory descriptors')
        distance(record['features'], record['features'])
    if not isinstance(record.get('provenance'), dict):
        raise ValueError('Memory provenance required')
    canonical(record)


class Memory:
    def __init__(self, path, read_only=False):
        self.path = Path(path)
        self.read_only = read_only
        if read_only:
            from urllib.parse import quote
            self.db = sqlite3.connect('file:' + quote(str(self.path.resolve())) + '?mode=ro', uri=True)
            if self.db.execute('PRAGMA application_id').fetchone()[0] != APPLICATION_ID:
                self.db.close()
                raise ValueError('Not an S-Eye memory database')
            self.verify()
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existed = self.path.exists()
        self.db = sqlite3.connect(self.path, timeout=10)
        application = self.db.execute('PRAGMA application_id').fetchone()[0]
        tables = self.db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if application not in (0, APPLICATION_ID) or (application == 0 and tables):
            self.db.close()
            raise ValueError('Refusing to modify an unrelated database')
        self.db.execute(f'PRAGMA application_id={APPLICATION_ID}')
        self.db.execute('CREATE TABLE IF NOT EXISTS observations (sequence INTEGER PRIMARY KEY, id TEXT UNIQUE NOT NULL, payload TEXT NOT NULL, sha256 TEXT NOT NULL)')
        self.db.commit()
        os.chmod(self.path, 0o600)

    def close(self):
        self.db.close()

    def verify(self):
        integrity = self.db.execute('PRAGMA quick_check').fetchone()[0]
        if integrity != 'ok':
            raise ValueError('SQLite integrity check failed')
        count = 0
        for identifier, payload, digest in self.db.execute('SELECT id,payload,sha256 FROM observations'):
            record = json.loads(payload)
            validate_record(record)
            if checksum(record) != digest or identifier != digest:
                raise ValueError('Observation checksum mismatch')
            count += 1
        return {'verified_observations': count, 'sqlite_integrity': integrity}

    def put(self, record):
        if self.read_only:
            raise PermissionError('Read-only memory cannot be modified')
        self.verify()
        validate_record(record)
        identifier = checksum(record)
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO observations(id,payload,sha256) VALUES (?,?,?)',
                            (identifier, canonical(record).decode(), identifier))
        return identifier

    def get(self, identifier):
        self.verify()
        row = self.db.execute('SELECT payload FROM observations WHERE id=?', (identifier,)).fetchone()
        return json.loads(row[0]) if row else None

    def search(self, features, limit=5):
        self.verify()
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError('Retrieval limit must be 1..100')
        distance(features, features)
        matches = []
        for identifier, payload in self.db.execute('SELECT id,payload FROM observations'):
            record = json.loads(payload)
            vector = record.get('features')
            if vector is not None and len(vector) == len(features):
                matches.append({'id': identifier, 'distance': distance(features, vector),
                                'provenance': record['provenance']})
        return sorted(matches, key=lambda row: (row['distance'], row['id']))[:limit]

    def recent(self, limit=20):
        self.verify()
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError('Browse limit must be 1..100')
        return [{'id': identifier, 'observation': json.loads(payload)} for identifier, payload in
                self.db.execute('SELECT id,payload FROM observations ORDER BY sequence DESC LIMIT ?', (limit,))]

    def export(self, path):
        self.verify()
        items = [json.loads(row[0]) for row in self.db.execute('SELECT payload FROM observations ORDER BY sequence')]
        payload = {'schema_version': 1, 'observations': items}
        atomic_json(path, {'payload': payload, 'sha256': checksum(payload)})
        return len(items)

    def import_file(self, path):
        if self.read_only:
            raise PermissionError('Read-only memory cannot be modified')
        self.verify()
        envelope = read_json(path)
        payload = envelope['payload']
        if checksum(payload) != envelope.get('sha256') or payload.get('schema_version') != 1:
            raise ValueError('Memory export checksum/schema mismatch')
        observations = payload.get('observations')
        if not isinstance(observations, list) or len(observations) > 100000:
            raise ValueError('Invalid memory import inventory')
        for record in observations:
            validate_record(record)
        with self.db:
            for record in observations:
                identifier = checksum(record)
                self.db.execute('INSERT OR IGNORE INTO observations(id,payload,sha256) VALUES (?,?,?)',
                                (identifier, canonical(record).decode(), identifier))
        return self.verify()

    def import_legacy_jsonl(self, path):
        if self.read_only:
            raise PermissionError('Read-only memory cannot be modified')
        self.verify()
        path = Path(path)
        if path.stat().st_size > 16 * 1024 * 1024:
            raise ValueError('Legacy import exceeds byte limit')
        original = path.read_bytes()
        records = [(number, json.loads(line)) for number, line in enumerate(original.splitlines(), 1) if line.strip()]
        if any(not isinstance(record, dict) for _, record in records):
            raise ValueError('Legacy observations must be objects')
        wrapped = [{'schema_version': 1, 'features': None, 'provenance': {'kind': 'legacy_jsonl',
                    'source_sha256': __import__('hashlib').sha256(original).hexdigest(), 'line': number},
                    'legacy_payload': record} for number, record in records]
        with self.db:
            for record in wrapped:
                identifier = checksum(record)
                self.db.execute('INSERT OR IGNORE INTO observations(id,payload,sha256) VALUES (?,?,?)',
                                (identifier, canonical(record).decode(), identifier))
        return len(wrapped)

    def retain(self, maximum):
        if self.read_only:
            raise PermissionError('Read-only memory cannot be modified')
        self.verify()
        if type(maximum) is not int or maximum < 0:
            raise ValueError('Retention maximum must be a nonnegative integer')
        with self.db:
            cursor = self.db.execute('DELETE FROM observations WHERE sequence NOT IN (SELECT sequence FROM observations ORDER BY sequence DESC LIMIT ?)', (maximum,))
        return cursor.rowcount
