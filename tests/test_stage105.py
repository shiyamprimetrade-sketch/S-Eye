import copy,unittest
from packet_fixtures import data,packet
from seye.learning.packet_prototypes import fit
from seye.learning.packet_calibration import bind,support
class CalibrationTests(unittest.TestCase):
    def test_model_bound_empirical_support_is_not_probability(self):
        train,val=data();model=fit(train,val);binding=bind(model,val);r=support(model,binding,packet(.01))
        self.assertEqual(r['validation_support_estimate'],1);self.assertIsNone(r['confidence_probability'])
    def test_training_rows_or_modified_model_are_rejected(self):
        train,val=data();model=fit(train,val)
        with self.assertRaises(ValueError):bind(model,train)
        binding=bind(model,val);changed=copy.deepcopy(model);changed['radii']['a']*=2
        with self.assertRaises(ValueError):support(changed,binding,packet(.01))
