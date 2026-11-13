import unittest
from seye.memory.scene_inventory import inventory
from test_stage125 import observation
class InventoryTests(unittest.TestCase):
    def test_nested_objects_have_geometry_without_names_or_clickability(self):
        r=inventory(observation([[5,5,80,60],[20,20,40,40]]));self.assertEqual(r['visual_hypothesis_count'],2)
        self.assertEqual(r['relations'][0]['containment'],'first_contains_second');self.assertIsNone(r['semantic_object_count'])
        self.assertTrue(all(x['semantic_label'] is None and x['clickability']=='unknown' for x in r['objects']))
    def test_no_objects_are_invented_from_frame_classification(self):
        r=observation([]);r['analysis'].update(label='run',accepted=True)
        self.assertEqual(inventory(r)['objects'],[])
        self.assertIsNone(inventory(r)['confidence_probability'])
