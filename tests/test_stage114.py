import tempfile,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from learning_batch_data import dataset
from seye.learning.packet_linear import fit,scores
from seye.learning.training_checkpoint import save,load
class CheckpointTests(unittest.TestCase):
    def test_inference_roundtrip_and_no_overwrite(self):
        d=dataset();m=fit(d['train'],d['validation'],epochs=5)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'model.json';save(path,m);restored=load(path)
            self.assertEqual(scores(m,d['validation'][0]['packet']),scores(restored,d['validation'][0]['packet']))
            self.assertEqual(m,restored)
            with self.assertRaises(FileExistsError):save(path,m)
    def test_corruption_rejected(self):
        d=dataset();m=fit(d['train'],d['validation'],epochs=2)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'model.json';save(p,m);p.write_text(p.read_text().replace('seye-packet-linear-v1','corrupted-kind'))
            with self.assertRaises(ValueError):load(p)
