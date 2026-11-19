import unittest
from PIL import Image,ImageDraw
from seye.interface.boundaries import contours

class BoundaryTests(unittest.TestCase):
    def test_concavity_and_hole_preserve_exact_area(self):
        image=Image.new('L',(12,12));d=ImageDraw.Draw(image);d.rectangle((1,1,9,9),fill=255);d.rectangle((3,3,6,6),fill=0)
        r=contours(image);self.assertEqual(r['net_area'],65);self.assertEqual([p['role'] for p in r['loops']],['outer','hole'])
        d.rectangle((1,7,5,9),fill=0);r=contours(image)
        self.assertEqual(r['net_area'],r['foreground_pixels'])
        self.assertTrue(all(x['points'][0]==x['points'][-1] for x in r['loops']))
    def test_diagonal_cells_border_and_budget(self):
        image=Image.new('L',(3,3));image.putpixel((0,0),255);image.putpixel((1,1),255)
        self.assertEqual(len(contours(image)['loops']),2)
        self.assertEqual(contours(image)['net_area'],2)
        with self.assertRaises(ValueError):contours(image,max_edges=4)
        self.assertEqual(contours(Image.new('L',(2,2)))['loops'],[])
