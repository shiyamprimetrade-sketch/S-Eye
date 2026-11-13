import tempfile,unittest
from pathlib import Path
from memory_fixtures import record
from seye.memory.store import Memory
from seye.memory.history import link,read
from seye.memory.transfer import export_bundle,restore_bundle
from seye.memory.retention import plan,apply
class RecoveryRetentionTests(unittest.TestCase):
    def test_verified_new_destination_recovery_and_history_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);m=Memory(root/'m.sqlite3');identifier=m.put(record(.1));link(m,'target',identifier,'s',0)
            export_bundle(m,root/'bundle.json');m.db.execute("UPDATE observations SET payload='{}'");m.db.commit()
            with self.assertRaises(ValueError):m.verify()
            r=restore_bundle(root/'bundle.json',root/'recovered.sqlite3');self.assertEqual(r['verified_observations'],1)
            recovered=Memory(root/'recovered.sqlite3',read_only=True)
            try:self.assertEqual(read(recovered,'target')['total'],1)
            finally:recovered.close();m.close()
            with self.assertRaises(FileExistsError):restore_bundle(root/'bundle.json',root/'recovered.sqlite3')
    def test_pins_stale_plan_and_link_cleanup_are_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:
                a=m.put(record(.1));b=m.put(record(.2));link(m,'target',b,'s',0);old=plan(m,1,[a]);m.put(record(.3))
                with self.assertRaises(ValueError):apply(m,old)
                self.assertEqual(m.verify()['verified_observations'],3)
                result=apply(m,plan(m,1,[a]));self.assertEqual(result['deleted_observations'],2);self.assertEqual(result['deleted_history_events'],1)
                self.assertEqual(read(m,'target')['events'],[]);self.assertIsNotNone(m.get(a))
            finally:m.close()
