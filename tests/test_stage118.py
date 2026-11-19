import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from compare_learning_batch import run
class ComparisonTests(unittest.TestCase):
    def test_three_methods_use_same_test_capture_identity(self):
        r=run();methods=r['methods'];self.assertEqual(set(methods),{'layout_prototype','centered_prototype','centered_sgd'})
        for m in methods.values():self.assertEqual((m['known_samples'],m['unknown_samples']),(6,4))
        self.assertEqual([x['id'] for x in methods['layout_prototype']['results']],[x['id'] for x in methods['centered_sgd']['results']])
    def test_preprocessing_and_training_results_are_separate(self):
        r=run();a=r['methods']['centered_prototype'];b=r['methods']['centered_sgd']
        self.assertIsNone(a['representative_application_accuracy']);self.assertIn('ablation',r['attribution'])
        self.assertEqual(a['known_correct'],b['known_correct'])
