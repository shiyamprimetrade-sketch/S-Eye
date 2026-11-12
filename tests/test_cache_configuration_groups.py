import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw
import analyze_image
from seye.core.configuration import load_config
from seye.recognition.cache import FeatureCache
from seye.scenes.relations import group_objects
from seye.integration.service import Permissions, handle
from seye.learning.prototypes import fit, save_model
from seye.recognition.features import extract


class CacheConfigurationTests(unittest.TestCase):
    def test_cache_reuses_descriptors_but_invalidates_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'image.png'
            image = Image.new('RGB', (100, 100), 'white'); ImageDraw.Draw(image).ellipse((20,20,80,80), outline='black', width=4); image.save(path)
            cache = FeatureCache(max_entries=1)
            a, provenance = cache.from_file(path); b, _ = cache.from_file(path)
            self.assertEqual(a, b); b[0] = 12345
            self.assertEqual(cache.from_file(path)[0], a)
            ImageDraw.Draw(image).rectangle((0,0,99,99), fill='black'); image.save(path)
            changed, current = cache.from_file(path)
            self.assertNotEqual(current['sha256'], provenance['sha256'])
            self.assertNotEqual(changed, a)
            self.assertEqual(cache.statistics()['misses'], 2)
            self.assertEqual(cache.statistics()['evictions'], 1)
            self.assertEqual(cache.statistics()['entries'], 1)

    def test_cache_budget_and_root_permission_still_apply_on_hits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'image.png'; Image.new('RGB', (20,20)).save(path)
            cache = FeatureCache(max_bytes=1); cache.from_file(path); self.assertEqual(cache.statistics()['entries'], 0)
            with self.assertRaisesRegex(ValueError, 'permitted'):
                cache.from_file(path, allowed_root=Path(directory)/'forbidden')
            with self.assertRaises(ValueError):
                FeatureCache(max_entries=True)

    def test_strict_configuration_and_lossless_explicit_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / 'config.json'
            path.write_text(json.dumps({'schema_version':0,'allowed_directory':str(root),'allow_memory':True}))
            before = path.read_bytes(); config = load_config(path)
            self.assertEqual(config['permissions'].read_roots, (str(root.resolve()),))
            self.assertEqual(config['permissions'].write_roots, ())
            self.assertTrue(config['permissions'].memory)
            self.assertEqual(path.read_bytes(), before)
            path.write_text(json.dumps({'schema_version':1,'read_roots':[str(root)],'video':'false'}))
            with self.assertRaises(ValueError):load_config(path)
            path.write_text(json.dumps({'schema_version':1,'unknown_option':True}))
            with self.assertRaises(ValueError):load_config(path)

    def test_proximity_groups_are_transitive_without_semantic_identity(self):
        rows = [{'class':'circle','box':[0,0,10,10]}, {'class':'triangle','box':[15,0,25,10]},
                {'class':'circle','box':[30,0,40,10]}, {'class':'circle','box':[100,0,110,10]}]
        result = group_objects(rows, maximum_gap=5)
        self.assertEqual(result['groups'], [[0,1,2],[3]])
        with self.assertRaises(ValueError):group_objects(rows, maximum_gap=-1)

    def test_batch_recognition_has_explicit_grants_and_reuses_features(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); a=Image.new('RGB',(100,100),'white');b=a.copy()
            ImageDraw.Draw(a).ellipse((20,20,80,80),outline='black',width=4)
            ImageDraw.Draw(b).polygon([(50,10),(10,90),(90,90)],outline='black',width=4)
            photo=root/'circle.png';a.save(photo)
            training=[{'id':'a','label':'circle','capture_group':'train-a','features':extract(a)},
                      {'id':'b','label':'triangle','capture_group':'train-b','features':extract(b)}]
            validation=[dict(row,capture_group='val-'+row['id']) for row in training]
            checkpoint=root/'model.json';save_model(checkpoint,fit(training,validation))
            request={'schema_version':1,'request_id':'batch','action':'recognize_batch',
                     'model':str(checkpoint),'images':[str(photo)]*3}
            response=handle(request,Permissions((str(root),),()))
            self.assertTrue(response['success'])
            self.assertEqual([r['label'] for r in response['result']['predictions']],['circle']*3)
            self.assertEqual(response['result']['cache']['hits'],2)
            self.assertFalse(handle(request,Permissions())['success'])

    def test_configuration_drives_the_cli_without_broadening_write_grants(self):
        import os, subprocess, sys
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); image=root/'image.png'; Image.new('RGB',(20,20),'white').save(image)
            request=root/'request.json';request.write_text(json.dumps({'schema_version':1,'request_id':'configured','action':'analyze','image':str(image)}))
            config=root/'config.json';config.write_text(json.dumps({'schema_version':1,'read_roots':[str(root)],'write_roots':[str(root)],'timeout':10}))
            output=root/'response.json'
            command=[sys.executable,'-m','seye.api.workflow','--request',str(request),'--output',str(output),'--config',str(config)]
            env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]/'src'))
            result=subprocess.run(command,capture_output=True,text=True,env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(json.loads(output.read_text())['success'])
            config.write_text(json.dumps({'schema_version':1,'read_roots':[str(root)],'write_roots':[]}))
            command[command.index(str(output))]=str(root/'denied-response.json')
            self.assertEqual(subprocess.run(command,capture_output=True,env=env).returncode,2)
            self.assertFalse((root/'denied-response.json').exists())
