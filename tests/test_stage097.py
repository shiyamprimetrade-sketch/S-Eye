import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageDraw
from seye.interface.localization import localize,decode_runs
from seye.interface.regions import edge_mask
from seye.detection.metrics import mask_iou
from seye.integration.service import handle,Permissions

class LocalizationTests(unittest.TestCase):
    def test_mask_matches_observed_edges_and_does_not_fill_region(self):
        image=Image.new('RGB',(100,70),'black');ImageDraw.Draw(image).rectangle((20,10,59,39),fill='white')
        r=localize(image);self.assertEqual(len(r['regions']),1)
        m=r['regions'][0]['mask'];decoded=decode_runs(m['source_size'],m['runs'])
        self.assertEqual(mask_iou(decoded,edge_mask(image)),1)
        self.assertEqual(decoded.getpixel((30,20)),0)
    def test_invalid_runs_and_scoped_adapter(self):
        for runs in ([[[0,2,1]]],):
            with self.assertRaises(ValueError):decode_runs([10,10],runs)
        with self.assertRaises(ValueError):decode_runs([10,10],[[1,1,5],[1,3,6]])
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);Image.new('RGB',(40,30)).save(root/'image.png')
            request={'schema_version':1,'request_id':'mask','action':'observe_interface','image':str(root/'image.png'),'region_proposals':True,'region_mode':'refined'}
            r=handle(request,Permissions((str(root),)));self.assertTrue(r['success'],r)
            self.assertEqual(r['result']['region_proposals']['method'],'paired_rectangular_boundaries_with_observed_edge_masks')
