import unittest
import analyze_image
from seye.learning.calibration_experiment import experiment


def row(identifier, score, expected):
    return {'id':identifier,'expected':expected,'prediction':{'candidates':[{'label':'a','raw_softmax_score':score}]}}


class ExperimentTests(unittest.TestCase):
    def test_test_outcomes_never_change_fitted_model(self):
        validation=[row('v1',.2,'b'),row('v2',.9,'a')]
        a=experiment(validation,[row('t1',.8,'a')])
        b=experiment(validation,[row('t1',.8,'b')])
        self.assertEqual(a['calibration_model'],b['calibration_model'])
        self.assertFalse(a['recognition_labels_changed'])
        self.assertNotEqual(a['calibrated_test_brier'],b['calibrated_test_brier'])

    def test_identity_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError,'leakage'):
            experiment([row('same',.8,'a')],[row('same',.7,'a')])
