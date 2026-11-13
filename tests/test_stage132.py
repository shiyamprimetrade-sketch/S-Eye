import unittest
from test_stage131 import view
from seye.scenes.spatial import relative_positions
class RelativePositionTests(unittest.TestCase):
    def test_scaled_source_and_boxes_preserve_normalized_geometry(self):
        a=relative_positions(view([[10,10,30,30],[60,40,80,60]]))
        b=relative_positions(view([[20,20,60,60],[120,80,160,120]],(200,160)))
        self.assertEqual(a['objects'],b['objects']);self.assertEqual(a['offsets'],b['offsets'])
    def test_missing_grid_abstains_without_assumed_dimensions(self):
        self.assertFalse(relative_positions(view([[0,0,10,10]],None))['comparable'])
