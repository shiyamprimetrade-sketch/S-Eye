import sys,unittest,tempfile,shutil
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from seye.video.resources import run_decoder,hash_file
from seye.video.sequence import observe_sequence
from seye.video.continuity import ContinuityTracker
from seye.video.interface import observe_video
from seye.integration.service import execute,Permissions

class VideoLimitsTests(unittest.TestCase):
    def test_source_stream_read_is_bounded_and_snapshot_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'input.mp4';source.write_bytes(b'abcdef')
            with (root/'copy.mp4').open('xb') as target:digest,count=hash_file(source,copy_to=target)
            self.assertEqual((digest,count),hash_file(root/'copy.mp4'))
            with self.assertRaises(ValueError):hash_file(source,maximum=3)
            for limit in (True,0,-1):
                with self.assertRaises(ValueError):hash_file(source,maximum=limit)

    def test_noisy_timeout_and_decoded_file_count_are_rejected(self):
        with self.assertRaises(ValueError):run_decoder([sys.executable,'-c','print("x"*70000)'],2)
        with self.assertRaises(ValueError):run_decoder([sys.executable,'-c','import time;time.sleep(5)'],.05)
        with tempfile.TemporaryDirectory() as directory:
            code='from pathlib import Path; p=Path('+repr(directory)+'); [(p/(str(i)+".png")).touch() for i in range(301)]'
            with self.assertRaises(ValueError):run_decoder([sys.executable,'-c',code],5,directory)

    def test_session_limit_numeric_edges_and_failed_update_preserve_state(self):
        t=ContinuityTracker(session_id='bounds')
        for i in range(300):t.update([],i/10,[100,80])
        before=deepcopy(t.__dict__)
        with self.assertRaises(ValueError):t.update([],30,[100,80])
        self.assertEqual(t.__dict__,before)
        for stamp in (1e10,5e-324):
            t=ContinuityTracker();t.update([],0,[100,80])
            with self.assertRaises(ValueError):t.update([],stamp,[100,80])
        samples=[{'detections':[],'timestamp':0,'source_size':[100,80]}]
        with self.assertRaises(ValueError):observe_sequence(samples*301,'a'*64)
        with self.assertRaises(ValueError):observe_sequence([{'detections':[{'class':'x','box':[0,0,1,1]}]*65,'timestamp':0,'source_size':[100,80]}],'a'*64)

    def test_permissioned_checkpoint_resume_and_exclusive_publication(self):
        samples=[{'detections':[{'class':'region','box':[10+i,10,30+i,30]}], 'timestamp':i/2,'source_size':[100,80]} for i in range(4)]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'track.json'
            request={'schema_version':1,'request_id':'temporal','action':'track_sequence','samples':samples[:2],
                     'source_sha256':'a'*64,'config':{'session_id':'integration'},'output_checkpoint':str(state)}
            with self.assertRaises(PermissionError):execute(request,Permissions())
            with self.assertRaises(PermissionError):execute(request,Permissions(video=True))
            permissions=Permissions(read_roots=(root,),write_roots=(root,),video=True,memory=True)
            first=execute(request,permissions)['result'];original=state.read_bytes()
            with self.assertRaises(FileExistsError):execute(request,permissions)
            self.assertEqual(state.read_bytes(),original)
            resumed=execute(dict(request,samples=samples[2:],checkpoint=str(state),output_checkpoint=None,config=None),permissions)['result']
            full=observe_sequence(samples,'a'*64,{'session_id':'integration'})
            self.assertEqual(first['frames']+resumed['frames'],full['frames'])
            self.assertEqual(resumed['checkpoint'],full['checkpoint'])
            self.assertIsNone(resumed['summary'])
            with self.assertRaises(ValueError):execute(dict(request,samples=samples[2:],checkpoint=str(state),output_checkpoint=None,config=None,source_sha256='b'*64),permissions)

    def test_dense_candidate_work_budget_rejects_without_returning_partial_evidence(self):
        rows=[{'class':'region','box':[10,10,30,30]} for _ in range(64)]
        samples=[{'detections':rows,'timestamp':i/10,'source_size':[100,80]} for i in range(6)]
        with self.assertRaisesRegex(ValueError,'candidate evidence budget'):
            observe_sequence(samples,'a'*64,{'max_missed':30})

    def test_out_of_view_interval_does_not_invent_a_fragmentation(self):
        from seye.video.evaluation import evaluate
        row={'class':'region','box':[1,1,10,10]}
        truth=[{'timestamp':i,'source_size':[100,80],'objects':([] if i==1 else [dict(row,gt_id='target')])} for i in range(4)]
        pred=[{'timestamp':i,'source_size':[100,80],'visible':([dict(row,track_uid='one')] if i in (0,3) else [])} for i in range(4)]
        r=evaluate(truth,pred)
        self.assertEqual(r['fn'],1)
        self.assertEqual(r['fragmentations'],0)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
    def test_actual_generated_encode_decode_keeps_failures_and_inputs(self):
        from benchmark_temporal_decode import run
        report=run()
        self.assertEqual(report['decoded_frames'],24)
        self.assertEqual(report['totals']['tp']+report['totals']['fn'],48)
        self.assertTrue(all(c['source_preserved'] for c in report['cases']))
        self.assertFalse(report['representative_validation'])
        with tempfile.TemporaryDirectory() as directory:
            clip=Path(directory)/'bad.mp4';clip.write_bytes(b'not a movie')
            with self.assertRaises(ValueError):observe_video(clip,directory,tracking_mode='conservative')
            self.assertEqual(clip.read_bytes(),b'not a movie')
