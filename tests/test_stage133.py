import unittest
from test_stage131 import view
from seye.scenes.grouping import aligned_groups
class AlignmentTests(unittest.TestCase):
    def test_row_chain_groups_with_explicit_edges(self):
        r=aligned_groups(view([[5,10,20,30],[25,10,40,30],[45,10,60,30],[70,50,90,70]]),maximum_gap=8)
        self.assertEqual(r['groups'],[[0,1,2],[3]]);self.assertEqual(len(r['links']),2)
    def test_containment_not_grouped_as_an_alignment_relation(self):
        r=aligned_groups(view([[0,0,100,80],[10,10,20,20]]));self.assertEqual(r['groups'],[[0],[1]])
        self.assertFalse(aligned_groups(view([],None))['complete'])
