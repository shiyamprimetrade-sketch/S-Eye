import unittest
from test_stage131 import view
from seye.scenes.uncertainty import assess
class UncertaintyTests(unittest.TestCase):
    def test_incomplete_and_ambiguous_inputs_keep_explicit_limits(self):
        value=view([[10,10,30,30]]);value.update(complete=False,source_sha256='a'*64)
        r=assess(value,{'comparable':True,'ambiguous_correspondence':True})
        self.assertEqual(r['state'],'partial_geometry');self.assertIn('correspondence_ambiguous',r['flags']);self.assertFalse(r['automatic_action_authorized'])
    def test_missing_source_and_viewport_comparison_are_not_confidence(self):
        r=assess(view([]),{'comparable':False})
        self.assertEqual(r['state'],'incomparable');self.assertIsNone(r['confidence_probability'])
        self.assertFalse(r['source_identity_available'])
