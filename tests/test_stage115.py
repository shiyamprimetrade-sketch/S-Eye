import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from learning_batch_data import dataset
from seye.learning.reproducibility import reproduce
from seye.learning.packet_linear import fit
class ReproducibilityTests(unittest.TestCase):
    def test_repeated_seed_reproduces_full_model(self):
        d=dataset();r=reproduce(d['train'],d['validation'],{'epochs':8,'seed':113,'learning_rate':.2})
        self.assertTrue(r['identical']);self.assertEqual(r['first_model_sha256'],r['second_model_sha256'])
    def test_different_seed_changes_initialization(self):
        d=dataset();a=fit(d['train'],d['validation'],epochs=2,seed=1);b=fit(d['train'],d['validation'],epochs=2,seed=2)
        self.assertNotEqual(a['initial_weights_sha256'],b['initial_weights_sha256'])
