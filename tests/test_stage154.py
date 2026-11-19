import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from memory_fixtures import record
from packet_fixtures import packet
from seye.memory.store import Memory
from seye.memory.packet_index import rebuild,query,query_many

class GroupedIndexTests(unittest.TestCase):
    def test_grouped_results_identical_and_only_one_authoritative_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:
                for value in (.1,.2,.3,.4):m.put(record(value))
                rebuild(m);packets=[packet(.12),packet(.35),packet(.4)]
                with patch.object(m,'verify',wraps=m.verify) as check:
                    grouped=query_many(m,packets,2)
                    self.assertEqual(check.call_count,1)
                self.assertEqual(grouped['queries'],[query(m,p,2) for p in packets])
                self.assertFalse(m.db.in_transaction)
                m.put(record(.6))
                with self.assertRaisesRegex(ValueError,'stale'):query_many(m,packets)
                self.assertFalse(m.db.in_transaction)
            finally:m.close()

    def test_corruption_rejected_and_caller_transaction_not_committed(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Memory(Path(directory)/'m.sqlite3')
            try:
                m.put(record(.1));rebuild(m)
                m.db.execute("UPDATE observations SET payload='{}'")
                self.assertTrue(m.db.in_transaction)
                with self.assertRaises(ValueError):query_many(m,[packet(.1)])
                self.assertTrue(m.db.in_transaction);m.db.rollback()
                self.assertEqual(query_many(m,[packet(.1)])['queries'][0]['matches'][0]['distance'],0)
                with self.assertRaises(ValueError):query_many(m,[packet(.1)]*33)
            finally:m.close()
