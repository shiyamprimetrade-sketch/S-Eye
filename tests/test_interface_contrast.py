from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw
from seye.interface.contrast import match_contrast
from seye.interface.observer import match_template
from seye.integration.service import Permissions,handle
from seye.detection.metrics import box_iou


def glyph(light=False):
    image=Image.new('RGB',(24,16),'white' if light else 'navy')
    ImageDraw.Draw(image).polygon([(6,3),(18,8),(6,13)],fill='black' if light else 'yellow')
    return image


class ContrastInterfaceTests(unittest.TestCase):
    def test_theme_and_scale_improve_without_replacing_pixel_baseline(self):
        screen=Image.new('RGB',(144,80),'gray');scaled=glyph(True).resize((36,24),Image.Resampling.NEAREST)
        screen.paste(scaled,(40,12));reference=glyph()
        self.assertEqual(match_template(screen,reference,min_similarity=1)['status'],'not_found')
        result=match_contrast(screen,reference,min_similarity=1)
        self.assertEqual(result['status'],'visual_candidate')
        self.assertEqual(result['candidate']['box'],[40,12,76,36])
        self.assertEqual(result['candidate']['scale'],1.5)

    def test_duplicates_across_scales_still_abstain(self):
        screen=Image.new('RGB',(208,128),'gray');screen.paste(glyph(),(40,12))
        screen.paste(glyph(True).resize((36,24),Image.Resampling.NEAREST),(136,60))
        result=match_contrast(screen,glyph(),min_similarity=1)
        self.assertEqual(result['status'],'ambiguous');self.assertIsNone(result['candidate'])

    def test_absent_low_contrast_and_stride_misalignment(self):
        blank=Image.new('RGB',(144,80),'gray')
        self.assertEqual(match_contrast(blank,glyph())['status'],'not_found')
        low=Image.new('RGB',(24,16),(120,120,120));ImageDraw.Draw(low).polygon([(6,3),(18,8),(6,13)],fill=(125,125,125))
        blank.paste(low,(40,12));self.assertEqual(match_contrast(blank,glyph())['status'],'not_found')
        blank=Image.new('RGB',(144,80),'gray');blank.paste(glyph(),(41,13))
        self.assertEqual(match_contrast(blank,glyph(),scales=[1],min_similarity=1)['status'],'not_found')

    def test_resource_and_configuration_validation(self):
        for scales in ([],[1,1],[True],[float('nan')],[.4],[2.1],[1]*6):
            with self.assertRaises(ValueError):match_contrast(Image.new('RGB',(96,64)),glyph(),scales=scales)
        with self.assertRaisesRegex(ValueError,'budget'):
            match_contrast(Image.new('RGB',(600,600)),glyph(),stride=4)
        with self.assertRaises(ValueError):match_contrast(Image.new('RGB',(96,64)),Image.new('RGB',(24,16),'white'))
        for value in (.8,True,float('inf')):
            with self.assertRaises(ValueError):match_contrast(Image.new('RGB',(96,64)),glyph(),min_similarity=value)

    def test_scoped_json_contract_and_default_contrast_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);glyph().save(root/'template.png')
            screen=Image.new('RGB',(144,80),'gray');screen.paste(glyph(True).resize((36,24),Image.Resampling.NEAREST),(40,12));screen.save(root/'screen.png')
            request={'schema_version':1,'request_id':'contrast','action':'observe_interface','matcher':'contrast',
                     'image':str(root/'screen.png'),'templates':[{'name':'run','path':str(root/'template.png')}],'scales':[1,1.5,2]}
            grants=Permissions((str(root),))
            result=handle(request,grants);self.assertTrue(result['success'],result)
            match=result['result']['elements'][0];self.assertEqual(match['status'],'visual_candidate')
            self.assertGreaterEqual(box_iou(match['candidate']['box'],[40,12,76,36]),.5)
            self.assertFalse(handle(request,Permissions())['success'])
            self.assertFalse(handle(dict(request,matcher='unknown'),grants)['success'])
            self.assertFalse(handle(dict(request,matcher='pixel'),grants)['success'])
