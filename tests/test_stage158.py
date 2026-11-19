import unittest,tempfile,sqlite3
from pathlib import Path
from memory_fixtures import record
from seye.memory.store import Memory
from seye.memory.packet_index import rebuild,query
from seye.memory.footprint import storage_report,snapshot,verify_snapshot

class StorageRecoveryTests(unittest.TestCase):
    def test_snapshot_reopens_with_records_index_and_source_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'original.sqlite3';m=Memory(path)
            try:
                rows=[record(.1),record(.2)];m.put_many(rows);rebuild(m)
                original=path.read_bytes();report=storage_report(m)
                self.assertEqual(report['observations'],2);self.assertGreater(report['derived_index_payload_bytes'],0)
                self.assertEqual(path.read_bytes(),original)
                target=Path(d)/'snapshot.sqlite3';receipt=snapshot(m,target)
                self.assertEqual(path.read_bytes(),original)
                reopened=Memory(target,read_only=True)
                try:self.assertEqual(query(m,rows[0]['packet']),query(reopened,rows[0]['packet']))
                finally:reopened.close()
                with self.assertRaises(FileExistsError):snapshot(m,target)
                with self.assertRaises(ValueError):verify_snapshot(target,'a'*64)
                self.assertEqual(verify_snapshot(target,receipt['snapshot_sha256'])['verified_observations'],2)
            finally:m.close()
            invalid=Path(d)/'invalid.sqlite3';invalid.write_bytes(b'invalid sqlite bytes'*50)
            with self.assertRaises(sqlite3.DatabaseError):Memory(invalid,read_only=True)
            invalid.unlink()

    def test_unfinished_transaction_and_corrupt_source_do_not_publish(self):
        with tempfile.TemporaryDirectory() as d:
            m=Memory(Path(d)/'source.sqlite3');target=Path(d)/'backup.sqlite3'
            try:
                m.put(record(.1));m.db.execute('BEGIN')
                with self.assertRaises(ValueError):snapshot(m,target)
                self.assertTrue(m.db.in_transaction);m.db.rollback()
                m.db.execute("UPDATE observations SET payload='{}'");m.db.commit()
                with self.assertRaises(ValueError):snapshot(m,target)
                self.assertFalse(target.exists())
                self.assertEqual(list(Path(d).glob('.seye-snapshot-*')),[])
            finally:m.close()
