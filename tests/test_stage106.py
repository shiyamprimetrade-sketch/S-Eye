import unittest
from packet_fixtures import data,packet
from seye.learning.packet_prototypes import fit
from seye.recognition.packet_decision import decide
class RejectionTests(unittest.TestCase):
    def test_known_and_distant_unknown(self):
        train,val=data();model=fit(train,val)
        self.assertTrue(decide(model,packet(.01))['accepted'])
        self.assertEqual(decide(model,packet(3))['reason'],'outside_validation_radius')
    def test_equal_category_support_abstains(self):
        train,val=data();model=fit(train,val);model['radii']={'a':1,'b':1}
        self.assertEqual(decide(model,packet(.5))['reason'],'ambiguous_known_categories')
        with self.assertRaises(ValueError):decide(model,packet(.1),min_margin=True)
