import unittest
from copy import deepcopy
from seye.video.continuity import ContinuityTracker

def row(x):return {'class':'region','box':[x,10,x+20,30]}

class ContinuityTests(unittest.TestCase):
    def test_velocity_and_reordering(self):
        t=ContinuityTracker()
        a=t.update([row(10),row(70)],0,[120,80])
        b=t.update([row(73),row(13)],1,[120,80])
        self.assertEqual([r['track_id'] for r in a['visible']],[1,2])
        self.assertEqual([r['box'][0] for r in b['visible']],[13,73])
        self.assertEqual(b['visible'][0]['motion']['velocity'],[3,0])
        self.assertFalse(b['semantic_identity_proven'])

    def test_ambiguity_abstains_instead_of_forcing_ids(self):
        t=ContinuityTracker()
        t.update([row(10),row(20)],0,[120,80])
        r=t.update([row(15)],1,[120,80])
        self.assertEqual(r['visible'],[])
        self.assertEqual(r['unresolved_detection_indices'],[0])
        self.assertEqual(r['retained_unobserved_ids'],[1,2])

    def test_bad_or_over_capacity_update_is_atomic(self):
        t=ContinuityTracker(max_tracks=1);t.update([row(10)],0,[120,80])
        before=deepcopy(t.__dict__)
        for rows in ([row(13),row(70)],[{'class':'region','box':[1,2,float('nan'),4]}]):
            with self.assertRaises(ValueError):t.update(rows,1,[120,80])
            self.assertEqual(t.__dict__,before)
