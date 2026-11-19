import unittest
from PIL import Image
from seye.memory.identity import pixel_identity,identify,occurrence
class IdentityTests(unittest.TestCase):
    def test_pixel_and_observation_identity_are_distinct(self):
        image=Image.new('RGB',(20,10),'red');digest=pixel_identity(image)
        record={'schema_version':1,'features':None,'analysis':{'source':{'pixel_sha256':digest}},'provenance':{'source_sha256':'a'*64}}
        r=identify(record);self.assertEqual(r['decoded_pixel_sha256'],digest);self.assertIsNone(r['model_sha256'])
        changed=dict(record,provenance={'source_sha256':'b'*64});self.assertNotEqual(r['observation_sha256'],identify(changed)['observation_sha256'])
        self.assertEqual(pixel_identity(image),digest)
    def test_occurrences_separate_sessions_and_validate_order_key(self):
        self.assertNotEqual(occurrence('a'*64,'one',0),occurrence('a'*64,'two',0))
        with self.assertRaises(ValueError):occurrence('a'*64,'one',True)
