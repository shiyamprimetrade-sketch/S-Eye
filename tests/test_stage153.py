import unittest
from PIL import Image,ImageDraw
from seye.recognition.pipeline import FeaturePipeline

class FeatureReuseTests(unittest.TestCase):
    def test_packets_identical_with_order_and_copy_isolation(self):
        image=Image.new('RGB',(100,80),'white');ImageDraw.Draw(image).rectangle((10,10,40,40),fill='black');before=image.tobytes()
        pipeline=FeaturePipeline();selections=[['shape'],['appearance','shape'],['shape','appearance']]
        actual=pipeline.extract_many(image,selections)
        self.assertEqual(actual['packets'],[pipeline.extract(image,s) for s in selections])
        self.assertEqual(actual['component_extractions'],2);self.assertEqual(actual['reused_component_requests'],3)
        actual['packets'][0]['features'][0]=123
        self.assertNotEqual(actual['packets'][2]['features'][0],123);self.assertEqual(image.tobytes(),before)

    def test_all_selections_validate_before_custom_function_runs(self):
        pipeline=FeaturePipeline();calls=[]
        pipeline.register('count','count-v1',1,lambda im:calls.append(1) or [1])
        with self.assertRaises(ValueError):pipeline.extract_many(Image.new('RGB',(10,10)),[['count'],['unknown']])
        self.assertEqual(calls,[])
        self.assertEqual(pipeline.extract_many(Image.new('RGB',(10,10)),[['count']]*4)['component_extractions'],1)
        self.assertEqual(len(calls),1)
