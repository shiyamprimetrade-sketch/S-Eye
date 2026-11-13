import copy,tempfile,unittest
from pathlib import Path
from packet_fixtures import data,packet
from seye.learning.packet_prototypes import fit,nearest,save,load
class PrototypeTests(unittest.TestCase):
    def test_fit_restore_and_schema_bound_predictions(self):
        train,val=data();model=fit(train,val);self.assertEqual(nearest(model,packet(.01))[0]['label'],'a')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'model.json';save(path,model);self.assertEqual(load(path),model)
            path.write_text(path.read_text().replace('seye-packet-prototypes-v1','damaged'))
            with self.assertRaises(ValueError):load(path)
    def test_group_content_and_identity_leakage_blocked(self):
        train,val=data()
        for key in ('id','group','content_sha256'):
            changed=copy.deepcopy(val);changed[0][key]=train[0][key]
            with self.assertRaises(ValueError):fit(train,changed)
