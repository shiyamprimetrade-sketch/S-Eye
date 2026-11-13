import tempfile,unittest
from pathlib import Path
from memory_fixtures import record
from seye.memory.store import Memory
from seye.memory.duplicates import groups
class DuplicateTests(unittest.TestCase):
    def test_file_pixel_and_feature_groups_are_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:
                for i in range(3):
                    r=record(.1);r['provenance'].update(source_sha256=('a' if i<2 else 'b')*64,pixel_sha256=('c' if i<2 else 'd')*64,event=i);m.put(r)
                r=groups(m);self.assertEqual(len(r['groups']['source_content']),1);self.assertEqual(len(r['groups']['decoded_pixels']),1)
                self.assertEqual(len(r['groups']['feature_equivalence'][0]['observations']),3);self.assertFalse(r['automatic_deletion'])
            finally:m.close()
    def test_missing_pixels_are_not_guessed(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:m.put(record(.1));self.assertEqual(groups(m)['groups']['decoded_pixels'],[])
            finally:m.close()
