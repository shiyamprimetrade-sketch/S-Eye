import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from learning_batch_data import dataset
from seye.learning.packet_linear import fit,scores
class TrainingTests(unittest.TestCase):
    def test_independent_sgd_updates_and_reduces_loss(self):
        d=dataset();m=fit(d['train'],d['validation'],epochs=20)
        self.assertLess(m['history'][-1]['training']['cross_entropy'],m['initial_training']['cross_entropy'])
        self.assertEqual(m['selected_by'],'validation_cross_entropy_only');self.assertFalse(m['pretrained_weights_used'])
        self.assertAlmostEqual(sum(scores(m,d['validation'][0]['packet'])),1)
    def test_budget_and_seed_contract(self):
        d=dataset()
        with self.assertRaises(ValueError):fit(d['train'],d['validation'],seed=True)
        with self.assertRaises(ValueError):fit(d['train'],d['validation'],epochs=10000)
