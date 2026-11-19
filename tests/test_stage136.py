import unittest
from test_stage131 import view
from seye.scenes.absence import missing_evidence
class AbsenceTests(unittest.TestCase):
    def test_consecutive_nonobservation_is_not_semantic_removal(self):
        a=view([[10,10,30,30]]);r=missing_evidence(a,[view([]),view([]),view([])])
        self.assertEqual(len(r['events']),1);self.assertEqual(r['events'][0]['consecutive_missing'],3);self.assertFalse(r['events'][0]['semantic_removal_proven'])
    def test_resize_and_covering_region_break_missing_support(self):
        a=view([[10,10,30,30]])
        self.assertEqual(missing_evidence(a,[view([]),view([],size=(200,80)),view([])])['events'],[])
        cover=view([[0,0,100,80]]);r=missing_evidence(a,[cover,cover]);self.assertEqual(r['events'],[])
        self.assertEqual(r['frames'][0]['regions'][0]['state'],'covered_or_relabelled_unknown')
