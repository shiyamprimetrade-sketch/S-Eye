import unittest
from seye.video.continuity import ContinuityTracker

def row(x):return {'class':'region','box':[x,10,x+20,30]}

class OcclusionTests(unittest.TestCase):
    def test_short_gap_has_tentative_reacquisition(self):
        t=ContinuityTracker(max_gap_seconds=3)
        t.update([row(10)],0,[120,80]);t.update([row(12)],.5,[120,80])
        missing=t.update([],1,[120,80]);r=t.update([row(16)],1.5,[120,80])
        self.assertEqual(missing['unobserved'][0]['reason'],'not_detected')
        self.assertFalse(missing['unobserved'][0]['occlusion_proven'])
        self.assertEqual(r['visible'][0]['track_id'],1)
        self.assertEqual(r['visible'][0]['association'],'tentative_reacquisition')
        self.assertEqual(r['visible'][0]['missed_samples_before_match'],1)

    def test_covering_region_abstains_and_expiration_is_bounded(self):
        t=ContinuityTracker(max_missed=1)
        t.update([row(10),row(50)],0,[120,80])
        cover={'class':'other','box':[5,5,80,40]}
        r=t.update([cover],.5,[120,80])
        self.assertEqual(r['visible'],[])
        self.assertEqual(r['unresolved_detection_indices'],[0])
        self.assertEqual(len(r['covering_evidence']),2)
        self.assertTrue(all(o['reason']=='possible_covering_observation' for o in r['unobserved']))
        r=t.update([cover],1,[120,80])
        self.assertEqual(r['retired_ids'],[1,2])
        r=t.update([row(10)],1.5,[120,80])
        self.assertEqual(r['visible'][0]['track_id'],3)
