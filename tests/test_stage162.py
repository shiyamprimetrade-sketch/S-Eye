import tempfile,unittest,hashlib
from pathlib import Path
from PIL import Image
from seye.api import Client,Permissions
from seye.integration.memory_adapter import MemoryAdapter

class MemoryAdapterTests(unittest.TestCase):
    def test_store_source_bound_read_only_query_and_refuse_changed_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'image.png';Image.new('RGB',(40,30),'white').save(path)
            client=Client(Permissions((root,),(root,),memory=True),isolated=False,strict=True)
            writable=MemoryAdapter(client,str(root/'memory.sqlite3'),writable=True)
            stored=writable.store_image(path,'store');self.assertTrue(stored['success'],stored)
            receipt=stored['result'];before=(root/'memory.sqlite3').read_bytes()
            read=MemoryAdapter(client,str(root/'memory.sqlite3'))
            fetched=read.observation(receipt['observation_id'],'fetch')
            self.assertEqual(fetched['result']['identity']['source_sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual((root/'memory.sqlite3').read_bytes(),before)
            with self.assertRaises(PermissionError):read.store_image(path,'blocked')
            wrong=writable.store_image(path,'wrong',expected_source_sha256='a'*64)
            self.assertFalse(wrong['success']);self.assertEqual((root/'memory.sqlite3').read_bytes(),before)

    def test_adapter_does_not_escalate_missing_memory_capability(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'image.png';Image.new('RGB',(30,30)).save(path)
            client=Client(Permissions((root,),(root,)),isolated=False)
            response=MemoryAdapter(client,str(root/'db.sqlite3'),True).store_image(path,'no-capability')
            self.assertFalse(response['success']);self.assertFalse((root/'db.sqlite3').exists())
