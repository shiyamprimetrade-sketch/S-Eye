import unittest
from PIL import Image,ImageDraw
from packet_fixtures import row
from seye.learning.annotations import validate_annotations
from seye.recognition.pipeline import FeaturePipeline
class AnnotationPreprocessTests(unittest.TestCase):
    def test_annotation_provenance_and_box_bounds(self):
        r=row('one',0,'a');r.update(annotation_origin='renderer',source_kind='generated',source_size=[20,20],box=[1,1,10,10])
        self.assertFalse(validate_annotations([r])['label_truth_authenticated'])
        r['box']=[0,0,30,10]
        with self.assertRaises(ValueError):validate_annotations([r])
    def test_centered_shape_removes_translation_without_changing_layout_schema(self):
        p=FeaturePipeline();packets=[]
        for x in (5,40):
            image=Image.new('RGB',(100,70),'black');ImageDraw.Draw(image).rectangle((x,10,x+19,29),fill='white')
            packets.append(p.extract(image,['shape']))
        self.assertEqual(packets[0],packets[1]);self.assertEqual(len(packets[0]['features']),257)
