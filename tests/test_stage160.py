import unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from seye.api import Client,Permissions,capabilities
from seye.core.storage import checksum
from seye.memory.store import Memory
from seye.memory.packet_index import rebuild
from memory_fixtures import record

class StableAPITests(unittest.TestCase):
    def test_default_denial_envelope_bounds_and_capabilities(self):
        client=Client(isolated=False)
        result=client.call('observe_interface','deny',image='/not-granted.png')
        self.assertFalse(result['success']);self.assertEqual(result['error']['type'],'PermissionError')
        self.assertFalse(capabilities()['v1_release']);self.assertNotIn('shell',capabilities()['actions'])
        for req in ({'schema_version':True,'request_id':'id','action':'analyze'},
                    {'schema_version':1,'request_id':'id','action':'shell'},
                    {'schema_version':1,'request_id':'id','action':[]},
                    {'schema_version':1,'request_id':'id','action':'analyze','extra':float('nan')}):
            with self.assertRaises(ValueError):client.request(req)
        with self.assertRaises(ValueError):Client(Permissions(memory='false'),isolated=False)

    def test_profile_batch_features_and_granted_memory_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'view.png';image=Image.new('RGB',(80,60),'white');ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(path)
            client=Client(Permissions(read_roots=(root,),write_roots=(root,),memory=True),isolated=False)
            args={'image':str(path),'region_proposals':True}
            plain=client.call('observe_interface','plain',**args);profile=client.call('profile_interface','profile',**args)
            self.assertEqual(plain['result'],profile['result']['observation'])
            result=client.call('extract_feature_batch','cache',images=[str(path)]*3,components=['shape'])
            self.assertTrue(result['success']);self.assertEqual(result['result']['cache']['hits'],2)
            sets=client.call('extract_feature_sets','sets',image=str(path),selections=[['shape'],['shape','appearance']])
            self.assertTrue(sets['success']);self.assertEqual(sets['result']['component_extractions'],2)
            m=Memory(root/'m.sqlite3');row=record(.1);m.put(row);rebuild(m);m.close()
            query=client.call('memory_packet_query_many','query',memory=str(root/'m.sqlite3'),packets=[row['packet']]*2)
            self.assertTrue(query['success']);self.assertEqual(query['result']['authoritative_inventory_verifications'],1)
            snap=client.call('memory_snapshot','snapshot',memory=str(root/'m.sqlite3'),output=str(root/'recovered.sqlite3'))
            self.assertTrue(snap['success']);self.assertTrue((root/'recovered.sqlite3').is_file())

    def test_spawned_client_uses_same_granted_request_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'blank.png';Image.new('RGB',(30,30),'white').save(path)
            request={'schema_version':1,'request_id':'worker','action':'observe_interface','image':str(path)}
            before=checksum(request)
            result=Client(Permissions(read_roots=(directory,)),timeout=20).request(request)
            self.assertTrue(result['success']);self.assertEqual(result['request_id'],'worker')
            self.assertEqual(checksum(request),before)
