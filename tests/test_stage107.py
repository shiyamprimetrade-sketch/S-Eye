import unittest
from packet_fixtures import data,packet
from seye.learning.packet_prototypes import fit
from seye.recognition.packet_decision import candidates
class CandidateTests(unittest.TestCase):
    def test_top_k_does_not_force_unknown_choice(self):
        t,v=data();m=fit(t,v);r=candidates(m,packet(3),top_k=1)
        self.assertFalse(r['selection']['accepted']);self.assertEqual(len(r['candidates']),1);self.assertTrue(r['truncated'])
        self.assertEqual(r['candidates'][0]['label_origin'],'training_records')
    def test_ties_are_deterministic_and_bound_checked(self):
        t,v=data();m=fit(t,v);r=candidates(m,packet(.5),top_k=10)
        self.assertEqual([x['label'] for x in r['candidates']],['a','b'])
        with self.assertRaises(ValueError):candidates(m,packet(.5),top_k=True)
