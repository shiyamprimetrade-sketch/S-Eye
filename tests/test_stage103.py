import copy,unittest
from PIL import Image
from seye.recognition.pipeline import FeaturePipeline
from seye.recognition.similarity import compare
class SimilarityTests(unittest.TestCase):
    def test_identity_and_symmetric_component_evidence(self):
        p=FeaturePipeline();a=p.extract(Image.new('RGB',(30,20),'red'),['geometry','appearance']);b=p.extract(Image.new('RGB',(30,20),'blue'),['geometry','appearance'])
        self.assertEqual(compare(a,a)['distance'],0);self.assertEqual(compare(a,b)['distance'],compare(b,a)['distance'])
        self.assertGreater(compare(a,b)['distance'],0);self.assertIsNone(compare(a,b)['confidence_probability'])
    def test_schema_and_nonfinite_rejection(self):
        p=FeaturePipeline();a=p.extract(Image.new('RGB',(30,20)),['geometry']);b=p.extract(Image.new('RGB',(30,20)),['appearance'])
        with self.assertRaises(ValueError):compare(a,b)
        b=copy.deepcopy(a);b['features'][0]=float('nan')
        with self.assertRaises(ValueError):compare(a,b)
        with self.assertRaises(ValueError):compare(a,a,{'geometry':True})
