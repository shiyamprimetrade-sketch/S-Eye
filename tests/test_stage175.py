import unittest,tempfile
from copy import deepcopy
from pathlib import Path
from PIL import Image
from seye.local.workspace import ingest,open_workspace
from seye.local.annotation_editor import new_draft,validate_draft,build_editor,safe_script_json

class AnnotationDraftTests(unittest.TestCase):
    def test_source_bound_boxes_and_review_status_cannot_be_forged(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'image.png';Image.new('RGB',(100,80),'white').save(source);ingest([source],root/'workspace',root)
            _,data,digest=open_workspace(root/'workspace',root);draft=new_draft(data,digest)
            draft['images'][0]['instances']=[{'id':'one','class':'interface_region','box':[10,10,90,70]}]
            self.assertEqual(validate_draft(draft,data,digest)['instances'],1)
            for field,value in (('sha256','a'*64),('annotation_status','human_reviewed')):
                bad=deepcopy(draft);bad['images'][0][field]=value
                with self.assertRaises(ValueError):validate_draft(bad,data,digest)
            bad=deepcopy(draft);bad['images'][0]['instances'][0]['box']=[10,10,101,70]
            with self.assertRaises(ValueError):validate_draft(bad,data,digest)

    def test_editor_is_standalone_unscored_and_script_data_escapes_markup(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'image.png';Image.new('RGB',(100,80),'white').save(source);ingest([source],root/'workspace',root)
            build_editor(root/'workspace',root/'editor',root)
            html=(root/'editor'/'annotate.html').read_text();self.assertIn('Download draft JSON',html);self.assertIn('data:image/png;base64,',html)
            self.assertNotIn('</script>',safe_script_json('</script><script>bad()'))
            self.assertIn('template_unscored',html)
