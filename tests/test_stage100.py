import tempfile
import unittest
from pathlib import Path
from PIL import Image
from seye.recognition.pipeline import FeaturePipeline
from seye.recognition.features import extract
from seye.integration.service import handle,Permissions

class FeaturePipelineTests(unittest.TestCase):
    def test_legacy_parity_and_versioned_composition(self):
        image=Image.new('RGB',(80,60),'gray');pipeline=FeaturePipeline()
        r=pipeline.extract(image,['legacy','interface']);self.assertEqual(r['features'][:91],extract(image))
        self.assertEqual(len(r['features']),114);self.assertEqual(r,pipeline.extract(image,['legacy','interface']))
        self.assertNotEqual(r['schema_sha256'],pipeline.extract(image,['interface'])['schema_sha256'])
    def test_plugin_isolation_dimensions_and_invalid_selection(self):
        p=FeaturePipeline();p.register('bad','v1',1,lambda image:[float('nan')])
        with self.assertRaises(ValueError):p.extract(Image.new('RGB',(10,10)),['bad'])
        with self.assertRaises(ValueError):p.register('legacy','v2',1,lambda image:[1])
        for names in (['interface','interface'],['missing'],[]):
            with self.assertRaises(ValueError):p.extract(Image.new('RGB',(10,10)),names)
    def test_read_only_scoped_feature_contract_and_caller_perspective(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);Image.new('RGB',(40,30),'gray').save(root/'image.png')
            request={'schema_version':1,'request_id':'features','action':'extract_features','image':str(root/'image.png'),
                     'components':['interface'],'perspective_quad':[[0,0],[39,0],[39,29],[0,29]]}
            r=handle(request,Permissions((str(root),)));self.assertTrue(r['success'],r)
            self.assertEqual(r['result']['schema']['dimension'],23)
            self.assertEqual(r['result']['normalization']['corner_origin'],'caller_supplied')
            self.assertFalse(handle(request,Permissions())['success'])
