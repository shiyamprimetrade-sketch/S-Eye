import unittest,tempfile
from pathlib import Path
from PIL import Image
from seye.api import Client,Permissions
from seye.integration.tools_adapter import ToolsAdapter,manifest

class ToolsTests(unittest.TestCase):
    def test_tool_map_is_observation_only_and_cannot_override_grants(self):
        adapter=ToolsAdapter(Client(isolated=False))
        for name,args in [('os.system',{}),('seye.click',{}),('seye.observe',{'image':'x','action':'train'}),('seye.observe',{'image':'x','command':'run'})]:
            with self.assertRaises(ValueError):adapter.invoke(name,args,'denied')
        with self.assertRaises(PermissionError):adapter.invoke('seye.observe',{'image':'x','memory':'x'},'write')
        self.assertEqual(manifest()['registration_in_main_s'],'not_deployed')

    def test_granted_image_returns_evidence_without_action_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'image.png';Image.new('RGB',(40,30),'white').save(path)
            adapter=ToolsAdapter(Client(Permissions((directory,)),isolated=False))
            result=adapter.invoke('seye.observe',{'image':str(path)},'observe')
            self.assertTrue(result['response']['success']);self.assertFalse(result['automatic_action_authorized'])
            self.assertTrue(result['output_is_untrusted_visual_data'])
