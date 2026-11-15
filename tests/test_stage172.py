import unittest,tempfile
from pathlib import Path
from PIL import Image
from seye.local.overlays import render,overlay_workspace
from seye.local.workspace import ingest
from seye.core.storage import read_json

class OverlayTests(unittest.TestCase):
    def test_half_open_edge_box_pixels_dimensions_and_source_preserved(self):
        image=Image.new('RGB',(40,30),'white');before=image.tobytes()
        result=render(image,[{'box':[0,0,40,30]}])
        self.assertEqual(result.size,(40,30));self.assertEqual(result.getpixel((39,29)),(255,170,20))
        self.assertEqual(result.getpixel((20,20)),(255,255,255));self.assertEqual(image.tobytes(),before)
        with self.assertRaises(ValueError):render(image,[{'box':[0,0,41,30]}])

    def test_workspace_overlay_metadata_and_source_files_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'source.png';Image.new('RGB',(60,40),'white').save(path)
            ingest([path],root/'workspace',root);before=(root/'workspace'/'images'/'0001.png').read_bytes()
            overlay_workspace(root/'workspace',root/'overlays',root)
            report=read_json(root/'overlays'/'manifest.json')['payload']
            self.assertEqual(report['items'][0]['source_size'],[60,40]);self.assertTrue((root/'overlays'/'image-0001.png').is_file())
            self.assertEqual((root/'workspace'/'images'/'0001.png').read_bytes(),before)
