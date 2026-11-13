import unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from seye.interface.observer import observe,observe_profiled
from seye.performance.trace import Trace

class LatencyTests(unittest.TestCase):
    def test_profiled_pixels_and_regions_equal_unprofiled_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.png';q=Path(d)/'b.png'
            a=Image.new('RGB',(100,80),'white');a.save(p);ImageDraw.Draw(a).rectangle((10,10,30,30),fill='black');a.save(q)
            options={'previous':p,'region_proposals':True,'region_mode':'refined'}
            actual=observe_profiled(q,**options)
            self.assertEqual(actual['observation'],observe(q,**options))
            rows=actual['performance']['stages'];self.assertEqual([r['name'] for r in rows],['decode_current','region_proposals','previous_decode_and_change'])
            self.assertTrue(all(r['success'] and r['wall_seconds']>=0 and r['process_cpu_seconds']>=0 for r in rows))
            rows[0]['name']='changed';self.assertNotEqual(Trace().report()['stages'],rows)

    def test_failure_is_recorded_and_reraised(self):
        trace=Trace()
        with self.assertRaises(RuntimeError):
            with trace.span('failing'):raise RuntimeError('expected')
        self.assertFalse(trace.report()['stages'][0]['success'])
