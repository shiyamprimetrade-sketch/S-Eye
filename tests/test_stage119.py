import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from compare_learning_batch import run
from seye.learning.regression import guard
class RegressionTests(unittest.TestCase):
    def test_measured_centered_fixture_floors_and_same_capture_guard(self):
        r=run()['methods'];self.assertEqual(r['centered_sgd']['known_correct'],6);self.assertEqual(r['centered_sgd']['unknown_rejected'],4)
        self.assertTrue(guard(r['layout_prototype'],r['centered_sgd'])['passed'])
    def test_falling_known_score_cannot_hide_behind_unknown_rejection(self):
        r=run()['methods']['centered_sgd'];bad=copy.deepcopy(r)
        bad['results'][0]['prediction'].update(label='__unknown__',accepted=False);bad['known_correct']-=1
        self.assertFalse(guard(r,bad)['passed'])
        bad=copy.deepcopy(r);bad['test_capture_sha256']='0'*64
        with self.assertRaises(ValueError):guard(r,bad)
