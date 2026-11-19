import copy,json,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageDraw
from seye.core.storage import checksum
from seye.core.probes import sha256
from seye.learning.versioning import snapshot,verify,diff,save

class DatasetVersionTests(unittest.TestCase):
    def fixture(self,root):
        image=Image.new('RGB',(60,50),'white');ImageDraw.Draw(image).rectangle((10,10,40,30),fill='black');image.save(root/'source.png')
        data={'schema_version':1,'dataset_id':'fixture','images':[{'id':'one','path':'source.png','sha256':sha256(root/'source.png'),'capture_group':'one','split':'train','label':'rectangle','source_kind':'synthetic','annotation_status':'generator'}]}
        (root/'manifest.json').write_text(json.dumps(data));return data
    def test_deterministic_revision_parent_label_diff_and_immutable_save(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);data=self.fixture(root);first=snapshot(root/'manifest.json','1.0.0')
            self.assertEqual(first,snapshot(root/'manifest.json','1.0.0'));self.assertEqual(verify(first,root)['verified_sources'],1)
            data['images'][0]['label']='box';(root/'manifest.json').write_text(json.dumps(data));second=snapshot(root/'manifest.json','1.1.0',first)
            self.assertEqual(diff(first,second)['labels_changed'],['one']);save(root/'revision.json',first)
            with self.assertRaises(FileExistsError):save(root/'revision.json',second)
            with self.assertRaises(ValueError):snapshot(root/'manifest.json','1.0.0',first)
    def test_changed_sources_duplicates_and_root_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);data=self.fixture(root);revision=snapshot(root/'manifest.json','1.0.0')
            duplicate=copy.deepcopy(data['images'][0]);duplicate.update(id='two',capture_group='two',split='test');data['images'].append(duplicate);(root/'manifest.json').write_text(json.dumps(data))
            with self.assertRaises(ValueError):snapshot(root/'manifest.json','1.0.1')
            Image.new('RGB',(60,50),'red').save(root/'source.png')
            with self.assertRaises(ValueError):verify(revision,root)
            data['images']=data['images'][:1];data['images'][0]['path']='../outside.png';(root/'manifest.json').write_text(json.dumps(data))
            with self.assertRaises(ValueError):snapshot(root/'manifest.json','2.0.0')
