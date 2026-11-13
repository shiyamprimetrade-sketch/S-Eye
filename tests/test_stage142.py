import unittest
from seye.video.motion import motion,common_translation

class MotionTests(unittest.TestCase):
    def test_irregular_time_size_and_caller_registration(self):
        r=motion([10,10,30,30],[16,12,40,36],2,[8,4])
        self.assertEqual(r['observed_displacement'],[8,4])
        self.assertEqual(r['velocity'],[4,2])
        self.assertEqual(r['size_delta'],[4,4])
        self.assertEqual(r['residual_displacement'],[0,0])
        self.assertIsNone(motion([0,0,2,2],[1,0,3,2],1)['residual_displacement'])
        for dt in (0,-1,True,float('nan')):
            with self.assertRaises(ValueError):motion([0,0,2,2],[1,0,3,2],dt)

    def test_median_does_not_claim_registration(self):
        pairs=[{'before':[0,0,10,10],'after':[dx,2,dx+10,12]} for dx in (3,3,40)]
        r=common_translation(pairs,1)
        self.assertEqual(r['median_displacement'],[3,2])
        self.assertEqual(r['residual_distances'],[0,0,37])
        self.assertFalse(r['registration_established'])
