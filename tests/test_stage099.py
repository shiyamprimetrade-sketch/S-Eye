import unittest
from PIL import Image,ImageDraw
from seye.interface.perspective import rectify

class PerspectiveTests(unittest.TestCase):
    def test_known_projective_corners_reproject(self):
        image=Image.new('RGB',(100,80),'white');quad=[[10,10],[80,16],[70,65],[20,60]]
        output,r=rectify(image,quad,(40,30));self.assertEqual(output.size,(40,30))
        self.assertLess(r['max_corner_reprojection_error'],1e-8)
        self.assertEqual(r['corner_origin'],'caller_supplied')
    def test_identity_and_invalid_geometry(self):
        image=Image.new('RGB',(30,20),'black');ImageDraw.Draw(image).rectangle((5,5,15,12),fill='red')
        output,r=rectify(image,[[0,0],[29,0],[29,19],[0,19]],(30,20))
        self.assertEqual(output.tobytes(),image.tobytes())
        for quad in ([[0,0]]*4,[[0,0],[29,19],[29,0],[0,19]],[[0,0],[30,0],[29,19],[0,19]]):
            with self.assertRaises(ValueError):rectify(image,quad)
