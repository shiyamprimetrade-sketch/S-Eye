import unittest
from seye.video.continuity import ContinuityTracker

def row():return {'class':'region','box':[10,10,30,30]}

class IdentityTests(unittest.TestCase):
    def test_namespaces_no_reuse_and_discontinuity(self):
        a,b=ContinuityTracker(session_id='a'),ContinuityTracker(session_id='b')
        first=a.update([row()],0,[100,80])['visible'][0]
        other=b.update([row()],0,[100,80])['visible'][0]
        self.assertNotEqual(first['track_uid'],other['track_uid'])
        r=a.update([row()],1,[200,160],discontinuity=True)
        self.assertEqual(r['visible'][0]['track_id'],2)
        self.assertEqual(r['retirements'],[{'track_id':1,'reason':'caller_discontinuity'}])

    def test_long_gap_starts_new_track_and_validates_session(self):
        t=ContinuityTracker(session_id='clip',max_gap_seconds=1)
        t.update([row()],0,[100,80])
        r=t.update([row()],2,[100,80])
        self.assertEqual(r['visible'][0]['track_uid'],'clip:2')
        self.assertEqual(r['retirements'][0]['reason'],'elapsed_gap_limit')
        for name in ('', 'a:b', 'x'*65):
            with self.assertRaises(ValueError):ContinuityTracker(session_id=name)
