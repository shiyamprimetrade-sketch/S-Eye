import tempfile,unittest
from pathlib import Path
from memory_fixtures import record
from seye.memory.store import Memory
from seye.memory.packet_index import rebuild,load_tree,project
class IndexTests(unittest.TestCase):
    def test_persistent_tree_and_freshness(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'memory.sqlite3';m=Memory(path);r=record(.1);m.put(r);result=rebuild(m);self.assertEqual(result['indexed_observations'],1)
            schema=r['packet']['schema_sha256'];self.assertEqual(load_tree(m,schema)['count'],1)
            m.put(record(.2))
            with self.assertRaisesRegex(ValueError,'stale'):load_tree(m,schema)
            m.close();m=Memory(path,read_only=True)
            try:
                with self.assertRaises(PermissionError):rebuild(m)
            finally:m.close()
    def test_cache_corruption_is_not_silently_used(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3');r=record(.1);m.put(r);rebuild(m)
            m.db.execute("UPDATE seye_packet_trees SET payload='{}'");m.db.commit()
            try:
                with self.assertRaises(ValueError):load_tree(m,r['packet']['schema_sha256'])
            finally:m.close()
