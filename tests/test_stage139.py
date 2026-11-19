import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from benchmark_scene_validation import run
class SceneValidationTests(unittest.TestCase):
    def test_full_oracle_matrix_keeps_all_samples_and_failures(self):
        r=run();self.assertEqual(r['pairs'],32);self.assertEqual(r['frames'],64)
        self.assertEqual(sum(v['pairs'] for v in r['by_state'].values()),32)
        self.assertFalse(r['representative_application_validation'])
        self.assertGreater(r['localization']['fn'],0)
    def test_grid_changes_are_explicit_abstentions(self):
        r=run();cases=[c for c in r['cases'] if c['state']=='viewport']
        self.assertEqual(len(cases),4);self.assertTrue(all(not c['comparison']['comparable'] for c in cases))
