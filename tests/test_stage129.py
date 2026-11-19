import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from benchmark_memory_quality import run
from memory_fixtures import record
from packet_fixtures import packet
from seye.memory.store import Memory
from seye.memory.packet_index import rebuild,query
class QualityTests(unittest.TestCase):
    def test_generated_category_quality_and_identity_ambiguity_are_separate(self):
        r=run();self.assertEqual((r['top1_category_correct'],r['category_recall_at3'],r['unknown_queries_without_match']),(6,6,4))
        self.assertEqual(r['ambiguous_known_queries'],6);self.assertFalse(r['representative_retrieval_quality_validated'])
    def test_one_result_limit_still_detects_equal_distance_ambiguity(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:
                a=record(.1);b=record(.1);b['provenance']['event']=2;m.put(a);m.put(b);rebuild(m)
                r=query(m,packet(.1),limit=1);self.assertEqual(len(r['matches']),1);self.assertTrue(r['ambiguous_top_distance'])
                self.assertEqual(query(m,packet(3),maximum_distance=.01)['matches'],[])
            finally:m.close()
