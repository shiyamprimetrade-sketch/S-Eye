import unittest
from PIL import Image,ImageDraw
from seye.interface.masks import repair_gaps

class RepairTests(unittest.TestCase):
    def test_one_pixel_gap_restored_without_mutating_source(self):
        image=Image.new('L',(25,12));ImageDraw.Draw(image).line((3,5,20,5),fill=255);image.putpixel((10,5),0)
        before=image.tobytes();r=repair_gaps(image)
        self.assertEqual(r['introduced_pixels'],1);self.assertEqual(r['mask'].getpixel((10,5)),255)
        self.assertEqual(image.tobytes(),before);self.assertTrue(r['may_join_distinct_regions'])
    def test_large_gap_is_not_hallucinated(self):
        image=Image.new('L',(10,4));image.putpixel((1,1),255);image.putpixel((5,1),255)
        self.assertEqual(repair_gaps(image,max_gap=1)['introduced_pixels'],0)
        with self.assertRaises(ValueError):repair_gaps(image,max_gap=4)
