import tempfile,unittest
from pathlib import Path
from memory_fixtures import record
from packet_fixtures import packet
from seye.memory.store import Memory
from seye.memory.packet_index import rebuild,query
from seye.recognition.similarity import compare
class RetrievalTests(unittest.TestCase):
    def test_exact_neighbors_match_exhaustive_and_prune_distances(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3');items=[]
            try:
                for i in range(64):
                    r=record(i/64);identifier=m.put(r);items.append((identifier,r))
                rebuild(m);p=packet(.41);r=query(m,p,limit=3)
                expected=sorted([{'id':i,'distance':compare(p,row['packet'])['distance']} for i,row in items],key=lambda r:(r['distance'],r['id']))[:3]
                self.assertEqual([v['id'] for v in r['matches']],[v['id'] for v in expected]);self.assertLess(r['distance_evaluations'],64)
                self.assertAlmostEqual(r['matches'][0]['distance'],expected[0]['distance'])
            finally:m.close()
    def test_explicit_source_exclusion_and_unknown_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3');r=record(.1)
            try:
                m.put(r);rebuild(m);self.assertEqual(query(m,packet(.1),exclude_sources=[r['provenance']['source_sha256']])['matches'],[])
                with self.assertRaises(ValueError):query(m,packet(.1),limit=True)
            finally:m.close()
