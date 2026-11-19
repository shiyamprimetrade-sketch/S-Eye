import unittest,tempfile
from pathlib import Path
from memory_fixtures import record
from seye.memory.store import Memory
from seye.local.memory_browser import page,export_page

class MemoryBrowserTests(unittest.TestCase):
    def test_pagination_snapshot_check_and_source_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'memory.sqlite3';memory=Memory(path);memory.put_many([record(i/10) for i in range(5)]);memory.close()
            before=path.read_bytes();a=page(path,root,limit=2);b=page(path,root,a['next_after'],2,a['inventory_sha256'])
            self.assertEqual([r['sequence'] for r in a['items']+b['items']],[1,2,3,4]);self.assertEqual(path.read_bytes(),before)
            memory=Memory(path);memory.put(record(.9));memory.close()
            with self.assertRaises(ValueError):page(path,root,b['next_after'],2,a['inventory_sha256'])

    def test_offline_export_escapes_untrusted_stored_content(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'memory.sqlite3';memory=Memory(path);r=record(.1);r['caller_label']='<script>bad()</script>';memory.put(r);memory.close()
            export_page(path,root/'browser',root)
            text=(root/'browser'/'memory.html').read_text()
            self.assertNotIn('<script>bad()',text);self.assertIn('&lt;script&gt;',text)
