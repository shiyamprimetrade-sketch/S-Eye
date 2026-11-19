import unittest
import analyze_image
from seye.learning.calibration import fit, estimate, brier


class CalibrationTests(unittest.TestCase):
    def test_monotonic_pooling_and_duplicate_scores(self):
        model=fit([.1,.2,.2,.8,.9],[False,True,False,False,True])
        values=[estimate(model,s)['validation_support_estimate'] for s in [0,.1,.2,.5,.8,.9,1]]
        self.assertEqual(values,sorted(values))
        self.assertEqual(model['samples'],5)
        self.assertIsNone(estimate(model,.8)['confidence_probability'])
        self.assertFalse(model['representative_validation'])

    def test_controlled_calibration_and_no_input_mutation(self):
        scores=[.2,.2,.8,.8];truth=[False,False,True,True]
        model=fit(scores,truth)
        calibrated=[estimate(model,s)['validation_support_estimate'] for s in scores]
        self.assertLess(brier(calibrated,truth),brier(scores,truth))
        self.assertEqual(scores,[.2,.2,.8,.8])

    def test_invalid_or_nonfinite_evidence_rejected(self):
        for scores,truth in [([],[]),([float('nan')],[True]),([True],[True]),([.5],[1]),([2],[False])]:
            with self.assertRaises(ValueError):fit(scores,truth)
