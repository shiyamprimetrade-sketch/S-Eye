import unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from seye.api import Client,Permissions
from seye.integration.memory_adapter import MemoryAdapter
from seye.integration.session import EyeSession,integration_requirements

class SessionIntegrationTests(unittest.TestCase):
    def test_end_to_end_explicit_store_index_find_question_share_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'image.png';image=Image.new('RGB',(80,60),'white');ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(path)
            client=Client(Permissions((root,),(root,),memory=True),isolated=False,strict=True)
            adapter=MemoryAdapter(client,str(root/'memory.sqlite3'),True)
            result=EyeSession(client,'session',adapter).run(path,persist=True,maximum_distance=0,include_self=True)
            self.assertTrue(result['success'],result)
            self.assertEqual([s['operation'] for s in result['steps']],['observe','store','index','find','question'])
            self.assertEqual(result['successful_write_steps'],['store','index'])
            self.assertEqual(result['steps'][3]['response']['result']['status'],'feature_candidate')
            self.assertFalse(result['automatic_action_authorized']);self.assertEqual(integration_requirements()['main_s_registration'],'not_deployed')

    def test_wrong_source_stops_before_memory_creation_and_default_is_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'image.png';Image.new('RGB',(40,30),'white').save(path)
            client=Client(Permissions((root,),(root,),memory=True),isolated=False,strict=True)
            adapter=MemoryAdapter(client,str(root/'memory.sqlite3'),True)
            session=EyeSession(client,'failure',adapter)
            failure=session.run(path,persist=True,expected_source_sha256='a'*64)
            self.assertFalse(failure['success']);self.assertEqual(len(failure['steps']),1);self.assertFalse((root/'memory.sqlite3').exists())
            read=session.run(path);self.assertTrue(read['success']);self.assertEqual(read['successful_write_steps'],[])
            self.assertFalse((root/'memory.sqlite3').exists())
