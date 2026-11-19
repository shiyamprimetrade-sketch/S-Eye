import unittest
from seye.scenes.spatial import frame,relationships

def view(boxes,size=(100,80)):
    return {'source_size':list(size) if size else None,'objects':[{'class':'interface_region','box':b} for b in boxes]}
class SpatialTests(unittest.TestCase):
    def test_topology_distinguishes_overlap_containment_touching_and_gap(self):
        for second,expected in [([10,10,20,20],'first_contains_second'),([25,25,50,50],'overlap'),([30,0,50,30],'touching'),([40,0,60,20],'disjoint')]:
            self.assertEqual(relationships(view([[0,0,30,30],second]))['relations'][0]['topology'],expected)
    def test_huge_nonfinite_or_outside_boxes_fail_explicitly(self):
        for box in ([0,0,10**1000,5],[0,0,float('nan'),5],[90,0,110,5]):
            with self.assertRaises(ValueError):frame(view([box]))
