import tempfile,unittest
from pathlib import Path
from memory_fixtures import record
from seye.memory.store import Memory
from seye.memory.provenance import summarize,audit
class ProvenanceTests(unittest.TestCase):
    def test_raw_score_never_becomes_truth_probability(self):
        r=record(.1);r['analysis']={'label':'run','accepted':True,'reason':'fixture','candidates':[{'label':'run','raw_softmax_score':.99}]}
        s=summarize(r);self.assertEqual(s['stored_label'],'run');self.assertIsNone(s['confidence_probability'])
        self.assertEqual(s['raw_candidate_scores'][0]['raw_softmax_score'],.99)
    def test_missing_historical_provenance_remains_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:
                m.put({'schema_version':1,'features':None,'provenance':{}});r=audit(m)
                self.assertEqual(r['missing_source_identity'],1);self.assertFalse(r['label_truth_authenticated'])
            finally:m.close()
