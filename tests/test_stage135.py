import unittest
from test_stage131 import view
from seye.scenes.changes import changes
class ChangeTests(unittest.TestCase):
    def test_movement_and_explicit_registration_are_separate(self):
        a=view([[10,10,50,40]]);b=view([[18,14,58,44]])
        self.assertEqual(changes(a,b)['events'][0]['kind'],'moved')
        r=changes(a,b,registration={'dx':8,'dy':4});self.assertEqual(r['events'][0]['kind'],'stable');self.assertEqual(r['registration_origin'],'caller')
    def test_resize_and_offscreen_registration(self):
        a=view([[10,10,50,40]]);b=view([[10,10,58,44]])
        self.assertEqual(changes(a,b)['events'][0]['kind'],'resized')
        with self.assertRaises(ValueError):changes(a,b,registration={'dx':100,'dy':0})
