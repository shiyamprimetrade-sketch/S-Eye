import unittest,tempfile,hashlib
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageDraw
from seye.integration.observations import observe_image
from seye.interface.observer import observe

class ImageRequestTests(unittest.TestCase):
    def test_expected_source_rejects_before_proposal_computation(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'image.png';Image.new('RGB',(40,30),'white').save(path)
            with patch('seye.integration.observations.observe') as call:
                with self.assertRaises(ValueError):observe_image(path,'a'*64)
                call.assert_not_called()

    def test_capture_is_not_redecoded_after_external_file_changes(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'image.png';image=Image.new('RGB',(80,60),'white');ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(path)
            original=hashlib.sha256(path.read_bytes()).hexdigest()
            def changed(*args,**kwargs):
                Image.new('RGB',(80,60),'black').save(path)
                return observe(*args,**kwargs)
            with patch('seye.integration.observations.observe',side_effect=changed):result=observe_image(path,original)
            self.assertEqual(result['identity']['source_sha256'],original)
            self.assertNotEqual(hashlib.sha256(path.read_bytes()).hexdigest(),original)
            self.assertEqual(result['observation']['source']['sha256'],original)
            self.assertFalse(result['automatic_action_authorized'])
