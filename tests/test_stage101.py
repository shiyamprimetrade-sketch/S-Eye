import unittest
from PIL import Image,ImageDraw
from seye.recognition.pipeline import FeaturePipeline

class GeometryTests(unittest.TestCase):
    def test_geometry_is_bounded_versioned_and_nonmutating(self):
        image=Image.new('RGB',(80,60),'black');ImageDraw.Draw(image).rectangle((10,10,49,39),fill='white');raw=image.tobytes()
        r=FeaturePipeline().extract(image,['geometry']);self.assertEqual(len(r['features']),12)
        self.assertGreater(r['features'][1],0);self.assertEqual(image.tobytes(),raw)
        self.assertEqual(r,FeaturePipeline().extract(image,['geometry']))
    def test_blank_has_zero_edge_mass(self):
        r=FeaturePipeline().extract(Image.new('RGB',(40,30),'white'),['geometry'])
        self.assertEqual(r['features'][2],0)
