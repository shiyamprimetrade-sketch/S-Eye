import unittest
from PIL import Image,ImageDraw
from seye.interface.masks import remove_specks

class NoiseTests(unittest.TestCase):
    def test_specks_removed_and_thin_long_stroke_preserved(self):
        image=Image.new('L',(30,20));d=ImageDraw.Draw(image);d.line((3,5,20,5),fill=255)
        image.putpixel((1,1),255);image.putpixel((27,17),255);before=image.tobytes()
        r=remove_specks(image);self.assertEqual(r['removed_pixels'],2);self.assertEqual(r['mask'].histogram()[255],18)
        self.assertEqual(image.tobytes(),before)
    def test_diagonal_connectivity_and_budget_policy(self):
        image=Image.new('L',(5,5));image.putpixel((1,1),255);image.putpixel((2,2),255)
        self.assertEqual(remove_specks(image,min_area=2)['removed_pixels'],0)
        with self.assertRaises(ValueError):remove_specks(image,min_area=True)
        with self.assertRaises(ValueError):remove_specks(Image.new('L',(500,500),255))
