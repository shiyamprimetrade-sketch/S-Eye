import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from learning_batch_data import dataset
from packet_glyph_experiment import render
from seye.learning.packet_linear import fit
from seye.learning.training_checkpoint import save
from seye.integration.service import handle,Permissions
from seye.memory.store import Memory
class TrainedObservationIntegrationTests(unittest.TestCase):
    def test_granted_scoped_inference_persists_and_denies_ungranted_memory(self):
        d=dataset();model=fit(d['train'],d['validation'],epochs=5)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);save(root/'model.json',model);render('run',52,20).save(root/'query.png')
            request={'schema_version':1,'request_id':'trained-memory','action':'recognize_trained','image':str(root/'query.png'),'model':str(root/'model.json'),'memory':str(root/'observations.sqlite3')}
            self.assertFalse(handle(request,Permissions((str(root),),(str(root),)))['success'])
            self.assertFalse((root/'observations.sqlite3').exists())
            response=handle(request,Permissions((str(root),),(str(root),),memory=True));self.assertTrue(response['success'],response)
            memory=Memory(root/'observations.sqlite3',read_only=True)
            try:
                saved=memory.get(response['result']['observation_id']);self.assertEqual(saved['packet']['schema_sha256'],model['schema_sha256'])
                self.assertIsNone(saved['analysis']['confidence_probability']);self.assertEqual(memory.verify()['verified_observations'],1)
            finally:memory.close()
