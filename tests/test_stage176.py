import unittest
from copy import deepcopy
from seye.local.comparison import compare


def report(identifier='a',sha='a'*64):
    return {'format':'seye-local-analysis-v1','schema_version':1,'workspace_sha256':'b'*64,'model_sha256':None,
            'items':[{'id':identifier,'source_sha256':sha,'source_size':[100,80],'region_count':1,'boxes':[[10,10,30,30]],
                      'decision':{'status':'not_requested','label':None,'confidence_probability':None}}]}

class ComparisonTests(unittest.TestCase):
    def test_changes_are_measured_without_inventing_accuracy(self):
        a=report();b=deepcopy(a);b['items'][0]['boxes'].append([50,50,70,70]);b['items'][0]['region_count']=2
        r=compare(a,b);self.assertEqual(r['items'][0]['region_count_delta'],1);self.assertIsNone(r['accuracy_change'])
        self.assertEqual(r['total_source_slots'],1)

    def test_partial_sources_stay_in_denominator_and_strict_mode_refuses_them(self):
        a=report();b=report('b')
        with self.assertRaises(ValueError):compare(a,b)
        partial=compare(a,b,True);self.assertEqual(partial['total_source_slots'],2);self.assertEqual(partial['incomparable_or_missing_slots'],2)
        mismatch=report(sha='c'*64)
        with self.assertRaises(ValueError):compare(a,mismatch)
        self.assertEqual(compare(a,mismatch,True)['items'][0]['status'],'incomparable_source')
