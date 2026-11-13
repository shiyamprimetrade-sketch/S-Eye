import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from packet_glyph_experiment import dataset,run
from seye.learning.packet_prototypes import fit
from seye.learning.packet_evaluation import evaluate
class EvaluationTests(unittest.TestCase):
    def test_complete_generated_counts_confusion_and_repeatability(self):
        r=run();self.assertEqual(r,run());report=r['report']
        self.assertEqual(report['samples'],10);self.assertEqual(report['known_samples'],6);self.assertEqual(report['unknown_samples'],4)
        self.assertEqual(sum(sum(row.values()) for row in report['confusion'].values()),10)
        self.assertIsNone(report['representative_application_accuracy'])
    def test_test_cannot_reuse_validation_records(self):
        d=dataset();m=fit(d['train'],d['validation'])
        with self.assertRaises(ValueError):evaluate(m,d['validation'])
