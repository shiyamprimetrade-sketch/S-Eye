"""Regression controls for local input, permissions and storage failure handling."""
import hashlib
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from seye.core.files import read_bounded, resolve_path
from seye.core.storage import atomic_json, read_json
from seye.image.ingestion import load_image
from seye.integration.service import Permissions, execute
from seye.local.profiles import migrate
from seye.memory.footprint import snapshot, verify_snapshot
from seye.memory.store import Memory
from seye.memory.transfer import export_bundle, restore_bundle


class HardeningTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_181_png_crc_mismatch_and_wrong_extension_are_rejected(self):
        path = self.root / 'good.png'
        Image.new('RGB', (20, 20)).save(path)
        self.assertEqual(load_image(path)[0].size, (20, 20))
        data = bytearray(path.read_bytes())
        position = data.index(b'IDAT')
        length = int.from_bytes(data[position-4:position], 'big')
        data[position + 4 + length] ^= 1
        corrupt = self.root / 'corrupt.png'
        corrupt.write_bytes(data)
        with self.assertRaises(ValueError):
            load_image(corrupt)
        alias = self.root / 'wrong.jpg'
        alias.write_bytes(path.read_bytes())
        with self.assertRaisesRegex(ValueError, 'extension'):
            load_image(alias)

    def test_182_regular_file_and_byte_limits(self):
        path = self.root / 'bytes'
        path.write_bytes(b'1234')
        self.assertEqual(read_bounded(path, 4), b'1234')
        with self.assertRaisesRegex(ValueError, 'byte limit'):
            read_bounded(path, 3)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            read_bounded(self.root, 4)
        if hasattr(os, 'mkfifo'):
            pipe = self.root / 'pipe'
            os.mkfifo(pipe)
            with self.assertRaisesRegex(ValueError, 'regular file'):
                read_bounded(pipe, 4)

    def test_183_cyclic_and_dangling_ancestors_are_rejected(self):
        link = self.root / 'link'
        try:
            link.symlink_to(link, target_is_directory=True)
        except OSError:
            self.skipTest('Symlink creation unavailable on this runner')
        with self.assertRaises(PermissionError):
            resolve_path(link / 'new' / 'file')
        link.unlink()
        link.symlink_to(self.root / 'missing', target_is_directory=True)
        with self.assertRaises(PermissionError):
            resolve_path(link / 'new' / 'file')
        self.assertEqual(resolve_path(self.root / 'new' / 'file'), self.root.resolve() / 'new' / 'file')

    def test_184_snapshot_requires_memory_and_an_independent_write_grant(self):
        source = self.root / 'source.db'
        target = self.root / 'backup.db'
        request = dict(schema_version=1, request_id='snapshot', action='memory_snapshot',
                       memory=str(source), output=str(target))
        with self.assertRaises(PermissionError):
            execute(request, Permissions((self.root,), (self.root,)))
        with self.assertRaises(PermissionError):
            execute(request, Permissions((self.root,), memory=True))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_185_memory_is_private_at_creation_and_read_only_enforced(self):
        source = self.root / 'source #%.db'
        memory = Memory(source)
        memory.close()
        before = source.read_bytes()
        if os.name == 'posix':
            self.assertEqual(stat.S_IMODE(source.stat().st_mode), 0o600)
        reader = Memory(source, read_only=True)
        try:
            with self.assertRaises(sqlite3.OperationalError):
                reader.db.execute('DELETE FROM observations')
            with self.assertRaises(PermissionError):
                reader.retain(0)
        finally:
            reader.close()
        self.assertEqual(source.read_bytes(), before)

    def test_186_abrupt_exit_rolls_back_uncommitted_database_change(self):
        source = self.root / 'source.db'
        memory = Memory(source)
        record = {'schema_version': 1, 'features': None, 'provenance': {'kind': 'test'}}
        try:
            identifier = memory.put(record)
        finally:
            memory.close()
        child = (
            "import os, sqlite3, sys; db = sqlite3.connect(sys.argv[1]); "
            "db.execute('BEGIN IMMEDIATE'); db.execute('DELETE FROM observations'); "
            "os._exit(23)"
        )
        result = subprocess.run([sys.executable, '-c', child, str(source)], timeout=15)
        self.assertEqual(result.returncode, 23)
        recovered = Memory(source)
        try:
            self.assertEqual(recovered.get(identifier), record)
            target = self.root / 'backup.db'
            receipt = snapshot(recovered, target)
            self.assertEqual(verify_snapshot(target, receipt['snapshot_sha256'])['verified_observations'], 1)
            target.with_name(target.name + '-wal').touch()
            with self.assertRaisesRegex(ValueError, 'standalone'):
                verify_snapshot(target, hashlib.sha256(target.read_bytes()).hexdigest())
        finally:
            recovered.close()

    def test_187_failed_publication_preserves_destination_and_cleans_temporary_file(self):
        path = self.root / 'data.json'
        atomic_json(path, {'old': True})
        with patch('seye.core.storage.os.fsync', side_effect=OSError('simulated sync failure')):
            with self.assertRaises(OSError):
                atomic_json(path, {'new': True}, overwrite=True)
        self.assertEqual(read_json(path), {'old': True})
        self.assertEqual(list(self.root.iterdir()), [path])
        memory = Memory(self.root / 'source.db')
        bundle = self.root / 'backup.json'
        try:
            export_bundle(memory, bundle)
        finally:
            memory.close()
        with patch('seye.memory.transfer.os.fsync', side_effect=OSError('simulated sync failure')):
            with self.assertRaises(OSError):
                restore_bundle(bundle, self.root / 'restored.db')
        self.assertFalse((self.root / 'restored.db').exists())
        self.assertEqual(list(self.root.glob('.seye-restore-*')), [])

    def test_188_invalid_migration_preserves_source_and_destination(self):
        source = self.root / 'legacy.json'
        output = self.root / 'current.json'
        atomic_json(source, {'schema_version': 0, 'allowed_directory': str(self.root),
                             'allow_memory': 'false'})
        before = source.read_bytes()
        with self.assertRaises(ValueError):
            migrate(source, output, self.root)
        self.assertEqual(source.read_bytes(), before)
        self.assertFalse(output.exists())
