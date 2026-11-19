import unittest
from seye.learning.diagnostics import overfitting
class DiagnosticTests(unittest.TestCase):
    def test_large_gap_warns_without_test_metrics(self):
        row={'epoch':1,'training':{'samples':10,'correct':10,'cross_entropy':.01},'validation':{'samples':10,'correct':2,'cross_entropy':2}}
        r=overfitting([row]);self.assertTrue(r['overfit_warning']);self.assertFalse(r['test_data_used'])
    def test_bad_histories_rejected(self):
        with self.assertRaises(ValueError):overfitting([])
        row={'epoch':1,'training':{'samples':1,'correct':1,'cross_entropy':float('nan')},'validation':{'samples':1,'correct':1,'cross_entropy':0}}
        with self.assertRaises(ValueError):overfitting([row])
