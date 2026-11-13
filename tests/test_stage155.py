import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from memory_fixtures import record
from seye.memory.store import Memory
from seye.interface.batch import observe_batch
from seye.integration.service import execute,Permissions

class BatchTests(unittest.TestCase):
    def test_atomic_insert_duplicates_bad_late_record_and_caller_rollback(self):
        with tempfile.TemporaryDirectory() as d:
            m=Memory(Path(d)/'m.sqlite3')
            try:
                with patch.object(m,'verify',wraps=m.verify) as v:
                    result=m.put_many([record(.1),record(.2),record(.1)])
                    self.assertEqual(v.call_count,1)
                self.assertEqual((result['inserted'],result['duplicates']),(2,1))
                with self.assertRaises(ValueError):m.put_many([record(.3),{'schema_version':True}])
                self.assertEqual(m.verify()['verified_observations'],2)
                m.db.execute('BEGIN');m.put_many([record(.4)])
                self.assertTrue(m.db.in_transaction);m.db.rollback()
                self.assertEqual(m.verify()['verified_observations'],2)
            finally:m.close()

    def test_mixed_batch_preserves_order_and_denies_all_paths_before_io(self):
        with tempfile.TemporaryDirectory() as d:
            good=Path(d)/'good.png';bad=Path(d)/'bad.png';Image.new('RGB',(40,30),'white').save(good);bad.write_bytes(b'broken')
            r=observe_batch([good,bad,good])
            self.assertEqual([i['success'] for i in r['items']],[True,False,True])
            self.assertEqual(r['decoded_pixels'],2400)
            request={'schema_version':1,'request_id':'batch','action':'observe_interface_batch','images':[str(good),str(Path(d).parent/'outside.png')]}
            with patch('seye.interface.batch.observe') as observe:
                with self.assertRaises(PermissionError):execute(request,Permissions(read_roots=(d,)))
                observe.assert_not_called()
