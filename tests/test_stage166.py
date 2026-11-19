import unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from seye.memory.store import Memory
from seye.memory.packet_index import rebuild
from seye.recognition.pipeline import FeaturePipeline
from seye.integration.observations import capture,prepare_record,persist
from seye.integration.retrieval import find

class RetrievalRequestTests(unittest.TestCase):
    def test_self_exclusion_unique_and_ambiguous_distance_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'image.png';image=Image.new('RGB',(60,40),'white');ImageDraw.Draw(image).rectangle((10,10,25,25),fill='black');image.save(path)
            m=Memory(root/'m.sqlite3')
            try:
                record=prepare_record(path,'self',['shape']);persist(m,record);rebuild(m)
                self.assertEqual(find(m,path,0)['status'],'no_match')
                self.assertEqual(find(m,path,0,include_self=True)['status'],'feature_candidate')
                record['provenance']['request_id']='duplicate';persist(m,record);rebuild(m)
                result=find(m,path,0,include_self=True)
                self.assertEqual(result['status'],'ambiguous');self.assertFalse(result['unique_semantic_identity'])
                self.assertFalse(result['automatic_action_authorized'])
                for cutoff in (-1,float('nan'),True):
                    with self.assertRaises(ValueError):find(m,path,cutoff)
            finally:m.close()
