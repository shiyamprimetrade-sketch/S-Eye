import unittest
from test_stage131 import view
from seye.scenes.comparison import compare_layout
class LayoutComparisonTests(unittest.TestCase):
    def test_resize_requires_explicit_normalized_comparison(self):
        a=view([[10,10,30,30]]);b=view([[20,20,60,60]],(200,160))
        self.assertFalse(compare_layout(a,b)['comparable'])
        r=compare_layout(a,b,normalize=True);self.assertEqual(r['geometric_similarity'],1);self.assertTrue(r['normalization_applied'])
    def test_equal_candidates_remain_ambiguous_and_missing_is_counted(self):
        a=view([[10,10,30,30],[60,10,80,30]]);b=view([[10,10,30,30],[10,10,30,30]])
        r=compare_layout(a,b);self.assertTrue(r['ambiguous_correspondence']);self.assertEqual(r['missing'],[1])
