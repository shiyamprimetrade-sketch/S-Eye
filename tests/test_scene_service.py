import tempfile
import unittest
from pathlib import Path
from seye.memory.store import Memory
from seye.integration.service import execute, Permissions
from test_stage125 import observation

class SceneServiceTests(unittest.TestCase):
    def test_read_only_scene_contracts(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'memory.sqlite3'
            m=Memory(path)
            a=m.put(observation([[10,10,30,30]])); b=m.put(observation([])); m.close()
            permissions=Permissions(read_roots=(directory,),memory=True)
            def call(action,**fields):
                return execute(dict(schema_version=1,request_id='scene-test',action=action,memory=str(path),**fields),permissions)
            self.assertFalse(call('scene_analyze',observation_id=a)['result']['uncertainty']['automatic_action_authorized'])
            self.assertTrue(call('scene_compare',before=a,after=b)['result']['comparable'])
            self.assertEqual(call('scene_changes',before=a,after=a)['result']['events'][0]['kind'],'stable')
            self.assertEqual(len(call('scene_absence',reference=a,observations=[b,b])['result']['events']),1)
            m=Memory(path,read_only=True);self.assertEqual(m.verify()['sqlite_integrity'],'ok');m.close()
