import unittest,tempfile
from pathlib import Path
from seye.core.storage import atomic_json,read_json
from seye.core.configuration import load_config,parse_config
from seye.local.profiles import initialize,migrate,inspect,difference

class ConfigWorkflowTests(unittest.TestCase):
    def test_version_zero_export_preserves_grants_and_original_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);old=root/'old.json';new=root/'new.json'
            atomic_json(old,{'schema_version':0,'allowed_directory':str(root),'allow_write':False,'allow_memory':True});before=old.read_bytes()
            result=migrate(old,new,root);self.assertEqual(result['from_version'],0);self.assertEqual(old.read_bytes(),before)
            diff=difference(load_config(old),load_config(new));self.assertEqual(diff['enabled_capabilities'],[]);self.assertEqual(diff['added_write_roots'],[])
            with self.assertRaises(FileExistsError):migrate(old,new,root)
            self.assertFalse(inspect(new,root)['applied'])

    def test_default_profile_does_not_grant_write_training_video_or_memory(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);initialize(root,root/'profile.json',root);data=read_json(root/'profile.json')
            self.assertEqual(data['write_roots'],[]);self.assertFalse(any(data[k] for k in ('memory','training','video')))
            for timeout in (True,0,float('nan')):
                with self.assertRaises(ValueError):parse_config(dict(data,timeout=timeout))
