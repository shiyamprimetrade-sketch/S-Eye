import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from learning_batch_data import dataset
from seye.learning.partitions import validate_partitions
class PartitionTests(unittest.TestCase):
    def test_complete_new_protocol_and_deterministic_fingerprint(self):
        d=dataset();r=validate_partitions(d);self.assertEqual(r['counts'],{'train':9,'validation':6,'test':10})
        self.assertEqual(r,validate_partitions(dataset()));self.assertFalse(r['near_duplicate_scene_independence_certified'])
    def test_each_identity_boundary_is_enforced(self):
        for field in ('id','group','content_sha256'):
            d=dataset();d['test'][0][field]=d['train'][0][field]
            with self.assertRaises(ValueError):validate_partitions(d)
