import tempfile,unittest
from pathlib import Path
from PIL import Image
from packet_fixtures import data,packet
from seye.recognition.explanation import explain
from seye.learning.packet_prototypes import fit,save
from seye.recognition.pipeline import FeaturePipeline
from seye.core.storage import checksum
from seye.integration.service import Permissions,handle
class ExplanationTests(unittest.TestCase):
    def test_difference_is_exact_and_unknown_reason_preserved(self):
        t,v=data();r=explain(fit(t,v),packet(.01));self.assertEqual(r['explanation']['largest_descriptor_differences'][0]['absolute_difference'],.01)
        self.assertFalse(explain(fit(t,v),packet(3))['selection']['accepted'])
    def test_scoped_model_image_contract(self):
        pipeline=FeaturePipeline();rows=[]
        for i,color in enumerate(('red','blue','red','blue')):
            image=Image.new('RGB',(30,20),color);p=pipeline.extract(image,['appearance'])
            rows.append({'id':str(i),'group':str(i),'content_sha256':checksum({'fixture':i}),'label':color,'packet':p})
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);save(root/'model.json',fit(rows[:2],rows[2:]));Image.new('RGB',(30,20),'red').save(root/'source.png')
            request={'schema_version':1,'request_id':'packet','action':'recognize_packet','image':str(root/'source.png'),'model':str(root/'model.json')}
            r=handle(request,Permissions((str(root),)));self.assertTrue(r['success'],r);self.assertEqual(r['result']['selection']['label'],'red')
            self.assertFalse(handle(request,Permissions())['success'])
