import unittest
from copy import deepcopy
from seye.video.continuity import ContinuityTracker
from seye.video.summary import summarize

class SummaryTests(unittest.TestCase):
    def test_source_bound_summary_keeps_gaps_and_endpoint_scope(self):
        t=ContinuityTracker(session_id='summary')
        row=lambda x:{'class':'region','box':[x,10,x+20,30]}
        frames=[t.update([row(10)],0,[100,80]),t.update([], .5,[100,80]),t.update([row(14)],1,[100,80])]
        r=summarize(frames,'a'*64);track=r['tracks'][0]
        self.assertEqual(track['visible_samples'],2)
        self.assertEqual(track['unobserved_samples'],1)
        self.assertEqual(track['tentative_reacquisitions'],1)
        self.assertEqual(track['sampled_endpoint_travel_pixels'],4)
        self.assertEqual(track['sample_span_seconds'],1)
        self.assertEqual(len(r['frames_sha256']),64)
        self.assertEqual(frames[-1]['visible'][0]['box'],[14,10,34,30])

    def test_unrelated_sessions_reuse_duplicate_ids_and_bad_order_fail(self):
        t=ContinuityTracker(session_id='one');row={'class':'region','box':[1,1,10,10]}
        a=t.update([row],0,[100,80]);b=t.update([row],1,[100,80])
        variants=[]
        bad=deepcopy(b);bad['session_id']='two';variants.append([a,bad])
        bad=deepcopy(b);bad['visible']*=2;variants.append([a,bad])
        variants.append([b,a])
        for frames in variants:
            with self.assertRaises(ValueError):summarize(frames,'a'*64)
        with self.assertRaises(ValueError):summarize([a]*301,'a'*64)
