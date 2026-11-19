import unittest
from seye.memory.scenes import compare_observations

def observation(boxes,size=(100,80)):
    return {'schema_version':1,'features':None,'provenance':{},'analysis':{'source':{'size':list(size)},'objects':[{'class':'interface_region','box':b} for b in boxes]}}
class SceneMemoryTests(unittest.TestCase):
    def test_missing_and_appeared_evidence(self):
        a=observation([[10,10,30,30],[60,10,80,30]]);b=observation([[10,10,30,30]])
        r=compare_observations(a,b);self.assertTrue(r['comparable']);self.assertEqual(len(r['matched']),1);self.assertEqual(len(r['missing']),1)
    def test_viewport_mismatch_abstains_and_bad_boxes_reject(self):
        a=observation([[10,10,30,30]]);b=observation([],size=(200,80));self.assertFalse(compare_observations(a,b)['comparable'])
        with self.assertRaises(ValueError):compare_observations(a,observation([[90,10,120,30]]))
