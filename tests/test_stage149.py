import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from seye.video.evaluation import evaluate
from benchmark_tracking_validation import run

class TrackingEvaluationTests(unittest.TestCase):
    def test_switches_missing_fragmentation_and_false_positives(self):
        row={'class':'region','box':[1,1,10,10]}
        truth=[{'timestamp':i,'source_size':[100,80],'objects':[dict(row,gt_id='target')]} for i in range(4)]
        pred=[{'timestamp':i,'source_size':[100,80],'visible':([] if i==1 else [dict(row,track_uid='a' if i==0 else 'b')])} for i in range(4)]
        pred[-1]['visible'].append({'class':'region','box':[50,50,60,60],'track_uid':'extra'})
        r=evaluate(truth,pred)
        self.assertEqual((r['tp'],r['fn'],r['fp'],r['identity_switches'],r['fragmentations']),(3,1,1,1,1))
        self.assertEqual(r['mota'],.25)
        pred[0]['visible']*=2
        with self.assertRaises(ValueError):evaluate(truth,pred)

    def test_matrix_keeps_failures_in_all_denominators(self):
        r=run()
        self.assertEqual(r['generated_sequences'],27)
        self.assertEqual(r['frames'],324)
        for method in ('legacy','conservative'):
            t=r['totals'][method]
            self.assertEqual(t['tp']+t['fn'],648)
            self.assertGreater(t['fn'],0)
            self.assertGreater(t['fp'],0)
        self.assertFalse(r['representative_validation'])
        self.assertTrue(any(c['unresolved_observations'] for c in r['cases']))
