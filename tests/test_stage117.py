import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from learning_batch_data import dataset
from seye.learning.curves import learning_curve
class CurveTests(unittest.TestCase):
    def test_increasing_counts_share_validation_and_no_test_access(self):
        d=dataset();r=learning_curve(d['train'],d['validation'],counts=[1,2],config={'epochs':5})
        self.assertEqual([p['training_samples'] for p in r['points']],[3,6]);self.assertFalse(r['test_data_used'])
    def test_unavailable_counts_are_not_invented(self):
        d=dataset()
        with self.assertRaises(ValueError):learning_curve(d['train'],d['validation'],counts=[4])
