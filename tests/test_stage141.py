import unittest
from seye.video.temporal import sampling_plan, frame_contract

class SamplingTests(unittest.TestCase):
    def test_grid_and_short_decode_contract(self):
        p = sampling_plan(3, 2)
        self.assertEqual(p['timestamps'], [i/3 for i in range(6)])
        self.assertEqual(p['maximum_frames'], 6)
        self.assertIn('not original', p['timestamp_scope'])
        for fps, seconds in ((True,2),(11,2),(2,31),(2,0)):
            with self.assertRaises(ValueError): sampling_plan(fps,seconds)

    def test_frame_contract_is_atomic_and_copied(self):
        rows=[{'class':'region','box':[1,2,10,20]}]
        r=frame_contract(rows,.5,[100,80],0)
        r[0]['box'][0]=3
        self.assertEqual(rows[0]['box'][0],1)
        for t in (0,-1,True,float('nan'),float('inf')):
            with self.assertRaises(ValueError): frame_contract(rows,t,[100,80],0)
        with self.assertRaises(ValueError): frame_contract(rows,1,[5,5])
        with self.assertRaises(ValueError): frame_contract(rows*65,1,[100,80])
