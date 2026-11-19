import unittest
from seye.video.performance import latency_report,track_samples

class PerformanceTests(unittest.TestCase):
    def test_known_latency_percentiles_and_invalid_measurements(self):
        r=latency_report([.04,.01,.03,.02],.2)
        self.assertEqual(r['frame_latency_seconds'],{'minimum':.01,'p50':.02,'p95':.04,'maximum':.04})
        self.assertEqual(r['tracking_frames_per_second'],20)
        self.assertIsNone(latency_report([0],0)['tracking_frames_per_second'])
        for values,wall in (([],1),([float('nan')],1),([1],-1),([True],1)):
            with self.assertRaises(ValueError):latency_report(values,wall)

    def test_measured_work_preserves_geometric_results_and_bounds(self):
        samples=[{'detections':[{'class':'region','box':[10+i,10,30+i,30]}], 'timestamp':i/2,'source_size':[100,80]} for i in range(10)]
        r=track_samples(samples,{'session_id':'profile'})
        self.assertEqual(len(r['frames']),10)
        self.assertEqual(r['candidate_edges'],9)
        self.assertEqual([f['visible'][0]['track_id'] for f in r['frames']],[1]*10)
        self.assertFalse(r['performance']['portable_speed_claim'])
        with self.assertRaises(ValueError):track_samples(samples*31)
