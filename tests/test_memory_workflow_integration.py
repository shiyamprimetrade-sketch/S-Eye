import json,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageDraw
from seye.core.storage import checksum
from seye.image.ingestion import load_image
from seye.recognition.pipeline import FeaturePipeline
from seye.memory.store import Memory
from seye.memory.identity import identify,pixel_identity
from seye.memory.provenance import summarize
from seye.memory.transfer import export_bundle,restore_bundle
from seye.memory.history import link
from seye.integration.service import Permissions,handle
class MemoryWorkflowIntegrationTests(unittest.TestCase):
    def test_scoped_build_query_and_read_only_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);image=Image.new('RGB',(80,60),'black');ImageDraw.Draw(image).rectangle((10,10,39,29),fill='white');image.save(root/'image.png')
            decoded,source=load_image(root/'image.png');source['pixel_sha256']=pixel_identity(decoded)
            path=root/'m.sqlite3';grants=Permissions((str(root),),(str(root),),memory=True)
            observed=handle({'schema_version':1,'request_id':'observe','action':'observe_interface','image':str(root/'image.png'),'memory':str(path)},grants)
            self.assertTrue(observed['success'],observed);identifier=observed['result']['observation_id']
            base={'schema_version':1,'request_id':'query','memory':str(path)}
            build=dict(base,action='memory_index_build');self.assertFalse(handle(build,Permissions((str(root),),(str(root),)))['success'])
            self.assertTrue(handle(build,grants)['success']);before=path.read_bytes()
            response=handle(dict(base,action='memory_packet_query',image=str(root/'image.png'),components=['shape']),grants)
            self.assertTrue(response['success'],response);self.assertEqual(response['result']['matches'][0]['id'],identifier);self.assertEqual(before,path.read_bytes())
    def test_null_historical_fields_stay_unknown(self):
        record={'schema_version':1,'features':None,'packet':None,'analysis':None,'provenance':{}}
        self.assertIsNone(identify(record)['feature_schema_sha256']);self.assertIsNone(summarize(record)['stored_label'])
        record['provenance']['source_sha256']='historical-text'
        self.assertIsNone(identify(record)['source_sha256']);self.assertTrue(identify(record)['identity_warnings'])
    def test_rehashed_bad_history_bundle_never_publishes_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);memory=Memory(root/'m.sqlite3');identifier=memory.put({'schema_version':1,'features':None,'provenance':{}});link(memory,'target',identifier,'s',0)
            export_bundle(memory,root/'bundle.json');memory.close();envelope=json.loads((root/'bundle.json').read_text())
            envelope['payload']['history'][0]['observation_id']='b'*64;envelope['sha256']=checksum(envelope['payload']);(root/'bad.json').write_text(json.dumps(envelope))
            with self.assertRaises(ValueError):restore_bundle(root/'bad.json',root/'recovered.sqlite3')
            self.assertFalse((root/'recovered.sqlite3').exists())
