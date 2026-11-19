import unittest
from seye.interface.grouping import pair_boundaries

class GroupingTests(unittest.TestCase):
    def test_pair_retains_outer_and_provenance(self):
        a={'box':[10,10,60,40]};b={'box':[12,12,58,38]}
        r=pair_boundaries([a,b]);self.assertEqual(r['output_count'],1)
        self.assertEqual(r['regions'][0]['box'],a['box']);self.assertEqual(r['regions'][0]['source_region_indices'],[0,1])
    def test_distinct_nested_or_adjacent_controls_remain_separate(self):
        rows=[{'box':[0,0,100,80]},{'box':[20,20,40,40]},{'box':[42,20,62,40]}]
        self.assertEqual(pair_boundaries(rows)['output_count'],3)
        with self.assertRaises(ValueError):pair_boundaries(rows,max_gap=True)
