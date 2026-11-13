import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw
from seye.interface.observer import change_regions, match_template, observe
from seye.integration.service import Permissions, handle
from seye.memory.store import Memory
from seye.core.capture_protocol import assess


def fixture():
    control = Image.new('RGB',(24,16),'navy')
    draw = ImageDraw.Draw(control)
    draw.rectangle((2,2,21,13),outline='white',width=2)
    draw.line((4,8,18,8),fill='yellow',width=2)
    return control


class InterfaceObserverTests(unittest.TestCase):
    def test_changed_regions_and_color_only_changes(self):
        before=Image.new('RGB',(96,64),'black');after=before.copy()
        ImageDraw.Draw(after).rectangle((32,16,47,31),fill='red')
        result=change_regions(before,after)
        self.assertEqual(result['regions'],[{'box':[32,16,48,32],'changed_tiles':1}])
        self.assertEqual(result['changed_pixels'],256)
        self.assertEqual(change_regions(before,before)['signal'],'pixels_unchanged')
        self.assertEqual(change_regions(before,after.resize((48,32)))['signal'],'viewport_changed')

    def test_templates_localize_and_abstain_on_duplicates(self):
        template=fixture();screen=Image.new('RGB',(96,64),'gray');screen.paste(template,(32,16))
        matched=match_template(screen,template,min_similarity=1)
        self.assertEqual(matched['candidate']['box'],[32,16,56,32])
        screen.paste(template,(64,32))
        self.assertEqual(match_template(screen,template,min_similarity=1)['status'],'ambiguous')
        self.assertIsNone(match_template(screen,template,min_similarity=1)['candidate'])
        self.assertEqual(match_template(Image.new('RGB',(96,64),'gray'),template)['status'],'not_found')

    def test_limits_and_low_information_templates(self):
        for template in (Image.new('RGB',(24,16),'white'),Image.new('RGB',(2,2))):
            with self.assertRaises(ValueError):match_template(Image.new('RGB',(96,64)),template)
        with self.assertRaisesRegex(ValueError,'budget'):
            match_template(Image.new('RGB',(1000,1000)),fixture(),stride=1)
        for invalid in (True,0,65):
            with self.assertRaises(ValueError):match_template(Image.new('RGB',(96,64)),fixture(),stride=invalid)
        with self.assertRaises(ValueError):change_regions(Image.new('RGB',(8,8)),Image.new('RGB',(8,8)),fraction=float('nan'))

    def test_scoped_integration_records_evidence_and_no_input_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);fixture().save(root/'template.png')
            before=Image.new('RGB',(96,64),'gray');before.save(root/'before.png')
            after=before.copy();after.paste(fixture(),(32,16));after.save(root/'after.png')
            request={'schema_version':1,'request_id':'ui-1','action':'observe_interface',
                     'image':str(root/'after.png'),'previous':str(root/'before.png'),
                     'templates':[{'name':'run_button','path':str(root/'template.png')}],
                     'memory':str(root/'memory.sqlite3'),'min_similarity':1}
            grants=Permissions((str(root),),(str(root),),memory=True)
            response=handle(request,grants);self.assertTrue(response['success'],response)
            result=response['result'];self.assertEqual(result['elements'][0]['candidate']['box'],[32,16,56,32])
            self.assertEqual(result['elements'][0]['name_origin'],'caller_supplied_template')
            memory=Memory(root/'memory.sqlite3',read_only=True)
            try:
                saved=memory.get(result['observation_id']);self.assertEqual(saved['analysis']['kind'],'interface_observation')
                self.assertEqual(memory.verify()['verified_observations'],1)
            finally:memory.close()
            self.assertFalse(handle(request,Permissions())['success'])
            self.assertFalse(handle(request,Permissions((str(root),),(str(root),)))['success'])
            self.assertFalse(handle(dict(request,action='click'),grants)['success'])
            request['templates'][0]['path']=str(root.parent/'outside.png')
            self.assertFalse(handle(request,grants)['success'])

    def test_observation_is_json_and_original_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'screen.png';Image.new('RGB',(96,64)).save(path)
            raw=path.read_bytes();result=observe(path)
            self.assertEqual(result['signals'],[{'type':'initial_observation'}])
            self.assertEqual(json.loads(json.dumps(result))['kind'],'interface_observation')
            self.assertEqual(raw,path.read_bytes())

    def test_owner_capture_only_policy_does_not_claim_labels_or_accuracy(self):
        rows=[dict(id=str(i),sha256=f'{i:064x}',source_kind='photograph',target_group='object',
                   lighting=['l1','l3','l8'][i],camera_angle=['r0','r30','r60'][i]) for i in range(3)]
        self.assertTrue(assess(rows,require_reviewed_labels=False)['ready'])
        self.assertFalse(assess(rows)['ready'])
        self.assertFalse(assess(rows,require_reviewed_labels=False)['recognition_accuracy_validated'])
        self.assertIsNone(assess(rows,require_reviewed_labels=False)['recognition_accuracy'])
        rows[1]['sha256']=rows[0]['sha256']
        self.assertFalse(assess(rows,require_reviewed_labels=False)['ready'])
