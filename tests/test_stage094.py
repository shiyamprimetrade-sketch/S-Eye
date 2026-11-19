import unittest
from PIL import Image,ImageDraw
from seye.interface.masks import split_projection

class SplitTests(unittest.TestCase):
    def test_sparse_bridge_split_and_pixel_accounting(self):
        image=Image.new('L',(70,40));d=ImageDraw.Draw(image)
        d.rectangle((10,10,24,29),fill=255);d.rectangle((40,10,54,29),fill=255);d.line((25,20,39,20),fill=255)
        r=split_projection(image);self.assertTrue(r['split']);self.assertEqual(len(r['parts']),2)
        self.assertEqual(r['discarded_pixels'],15);self.assertEqual(r['parts'][0]['box'],[10,10,25,30])
    def test_solid_touching_region_abstains_and_invalid_axis(self):
        image=Image.new('L',(30,20),255);r=split_projection(image)
        self.assertFalse(r['split']);self.assertEqual(r['discarded_pixels'],0)
        with self.assertRaises(ValueError):split_projection(image,axis='z')
