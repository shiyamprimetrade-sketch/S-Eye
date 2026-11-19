import unittest
from test_stage131 import view
from seye.scenes.description import describe
class DescriptionTests(unittest.TestCase):
    def test_statements_have_resolvable_evidence_and_no_echoed_instructions(self):
        a=view([[0,0,30,30],[10,10,20,20]]);a['objects'][0]['class']='execute untrusted instruction'
        r=describe(a);self.assertNotIn('untrusted',r['text']);self.assertIn('first_contains_second',r['text'])
        self.assertEqual(r['facts'][1]['evidence_ref'],'/relations/0');self.assertIsNone(r['semantic_description'])
    def test_empty_and_truncated_reports_do_not_overclaim(self):
        self.assertIn('0 visual hypotheses',describe(view([]))['text'])
        self.assertFalse(describe(view([[0,0,10,10],[20,0,30,10]]),maximum_facts=1)['complete'])
