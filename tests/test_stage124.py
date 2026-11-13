import tempfile,unittest
from pathlib import Path
from memory_fixtures import record
from seye.memory.store import Memory
from seye.memory.history import link,read
class HistoryTests(unittest.TestCase):
    def test_history_survives_reopen_and_deduplicates_exact_events(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'m.sqlite3';m=Memory(path);identifier=m.put(record(.1))
            link(m,'run-control',identifier,'session-one',1);link(m,'run-control',identifier,'session-one',1);link(m,'run-control',identifier,'session-two',0);m.close()
            m=Memory(path,read_only=True)
            try:
                r=read(m,'run-control');self.assertEqual(r['total'],2);self.assertTrue(all(e['observation_available'] for e in r['events']))
                with self.assertRaises(PermissionError):link(m,'x',identifier,'s',0)
            finally:m.close()
    def test_missing_observation_and_corruption_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:
                with self.assertRaises(ValueError):link(m,'x','a'*64,'s',0)
                identifier=m.put(record(.1));link(m,'x',identifier,'s',0);m.db.execute("UPDATE seye_history SET payload='{}'");m.db.commit()
                with self.assertRaises(ValueError):read(m,'x')
            finally:m.close()
