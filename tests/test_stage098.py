import unittest
from PIL import Image,ImageDraw
from seye.interface.overlap import visible_regions
from seye.interface.localization import decode_runs
from seye.detection.metrics import mask_iou

class OverlapTests(unittest.TestCase):
    def test_two_color_overlap_preserves_only_visible_pixels(self):
        image=Image.new('RGB',(100,70),'black');d=ImageDraw.Draw(image)
        d.rectangle((10,10,49,39),fill='red');d.rectangle((30,20,69,49),fill='blue')
        r=visible_regions(image);self.assertEqual(len(r['regions']),2);self.assertEqual(len(r['overlaps']),1)
        self.assertEqual(sorted(x['visible_pixels'] for x in r['regions']),[800,1200])
        self.assertEqual(r['overlaps'][0]['depth_order'],'unknown')
        red=next(x for x in r['regions'] if x['visible_pixels']==800)
        mask=decode_runs(red['mask']['source_size'],red['mask']['runs'])
        self.assertEqual(mask.getpixel((35,25)),0)
    def test_same_color_overlap_is_not_claimed_as_two_instances(self):
        image=Image.new('RGB',(100,70),'black');d=ImageDraw.Draw(image)
        d.rectangle((10,10,49,39),fill='red');d.rectangle((30,20,69,49),fill='red')
        self.assertEqual(len(visible_regions(image)['regions']),1)
