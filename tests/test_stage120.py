import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from learning_batch_data import dataset
from seye.learning.packet_linear import fit
from seye.recognition.trained import predict
from seye.memory.packet_observations import remember
from seye.memory.store import Memory,validate_record
class ObservationTests(unittest.TestCase):
    def test_packet_observation_reopens_verifies_and_keeps_no_image_bytes(self):
        d=dataset();m=fit(d['train'],d['validation'],epochs=5);p=d['validation'][0]['packet'];r=predict(m,p);r['source']={'sha256':'a'*64}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'memory.sqlite3';receipt=remember(path,'request',p,r)
            memory=Memory(path,read_only=True)
            try:
                stored=memory.get(receipt['observation_id']);self.assertEqual(stored['packet'],p);self.assertIsNone(stored['features'])
                self.assertEqual(memory.verify()['verified_observations'],1);self.assertNotIn('image',stored)
                stored['provenance']['source_sha256']='b'*64
                with self.assertRaises(ValueError):validate_record(stored)
            finally:memory.close()
    def test_read_only_memory_cannot_append(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'memory.sqlite3';m=Memory(path);m.close();m=Memory(path,read_only=True)
            try:
                with self.assertRaises(PermissionError):m.put({'schema_version':1,'features':None,'provenance':{}})
            finally:m.close()
