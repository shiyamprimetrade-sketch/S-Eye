import unittest
from PIL import Image
from seye.recognition.pipeline import FeaturePipeline
class AppearanceTests(unittest.TestCase):
    def test_histograms_and_constant_texture(self):
        r=FeaturePipeline().extract(Image.new('RGB',(40,30),'red'),['appearance'])['features']
        self.assertEqual(len(r),30);self.assertEqual(r[3],1);self.assertEqual(r[12:14],[0,0])
        for i in (0,4,8):self.assertEqual(sum(r[i:i+4]),1)
    def test_schema_distinguishes_features(self):
        p=FeaturePipeline();image=Image.new('RGB',(40,30),'red')
        self.assertNotEqual(p.extract(image,['geometry'])['schema_sha256'],p.extract(image,['appearance'])['schema_sha256'])
