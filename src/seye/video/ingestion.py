"""Bounded local prerecorded decoding; independent geometric observations only."""
import json
from pathlib import Path
import shutil
import tempfile
import time
from seye.detection.analysis import analyze
from seye.video.tracking import Tracker
from seye.video.temporal import sampling_plan
from seye.video.resources import hash_file, run_decoder, MAX_VIDEO_BYTES


def analyze_video(path, allowed_root, fps=2, max_seconds=30, mode='baseline', temporal_details=False):
    path, allowed_root = Path(path).resolve(), Path(allowed_root).resolve()
    if not path.is_relative_to(allowed_root) or not path.is_file() or path.suffix.lower() not in ('.mp4','.mov','.mkv','.avi'):
        raise ValueError('Permitted local video file required')
    plan=sampling_plan(fps,max_seconds)
    if type(temporal_details) is not bool:raise ValueError('Boolean temporal_details required')
    if path.stat().st_size>MAX_VIDEO_BYTES:raise ValueError('Video exceeds 128 MiB')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('Optional local ffmpeg/ffprobe executables required')
    start=time.perf_counter();tracker=Tracker();frames=[];analysis_seconds=0
    with tempfile.TemporaryDirectory(prefix='seye_video_') as directory:
        root=Path(directory);snapshot=root/('input'+path.suffix.lower());decoded=root/'frames';decoded.mkdir()
        # Decode the exact bytes whose digest is recorded, even if the original
        # file is changed concurrently. No whole-video Python byte allocation.
        with snapshot.open('xb') as target:initial_hash,source_bytes=hash_file(path,copy_to=target)
        before=time.perf_counter()
        common=['-v','error','-max_alloc','67108864','-protocol_whitelist','file,pipe',
                '-format_whitelist','mov,matroska,webm,avi']
        raw=run_decoder(['ffprobe',*common,'-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(snapshot)],10)
        probe_seconds=time.perf_counter()-before
        streams=json.loads(raw).get('streams',[])
        if not streams:raise ValueError('Video stream required')
        width,height=streams[0].get('width'),streams[0].get('height')
        if any(type(v) is not int or not 1<=v<=8192 for v in (width,height)) or width*height>20_000_000:
            raise ValueError('Unsupported video dimensions')
        before=time.perf_counter()
        run_decoder(['ffmpeg',*common,'-nostdin','-threads','1','-filter_threads','1',
                     '-i',str(snapshot),'-t',str(max_seconds),'-vf',f'fps={fps},scale=300:400:force_original_aspect_ratio=decrease',
                     '-frames:v',str(plan['maximum_frames']),'-threads','1',str(decoded/'%06d.png')],60,decoded)
        decode_seconds=time.perf_counter()-before
        files=sorted(decoded.glob('*.png'))
        if not files or len(files)>plan['maximum_frames']:raise ValueError('Invalid decoded frame count')
        for index,frame in enumerate(files):
            before=time.perf_counter()
            report,artifacts=analyze(frame,mode)
            if artifacts['source'].width*artifacts['source'].height>120000:raise ValueError('Decoded dimensions exceed grid cap')
            detections=[{'class':row['class'],'box':row['source_box']} for row in report['objects']]
            observation=tracker.update(detections,plan['timestamps'][index])
            if temporal_details:
                observation.update(source_size=report['source']['size'],sample_index=index,
                                   decoded_frame_sha256=report['source']['sha256'])
            frames.append(observation);analysis_seconds+=time.perf_counter()-before
        if hash_file(path)[0]!=initial_hash:raise ValueError('Video source changed during decode')
        decoded_bytes=sum(f.stat().st_size for f in files)
    seconds=time.perf_counter()-start
    history={}
    for frame in frames:
        for obj in frame['visible']:history.setdefault(obj['track_id'],[]).append(frame['timestamp'])
    summaries=[{'track_id':identifier,'first_seen':times[0],'last_seen':times[-1],'sampled_observations':len(times)} for identifier,times in sorted(history.items())]
    return {'schema_version':1,'source_sha256':initial_hash,'source_bytes':source_bytes,'track_summaries':summaries,
            'sample_fps':fps,'timestamp_scope':plan['timestamp_scope'],'frames':frames,'processed_frames':len(frames),
            'wall_seconds':seconds,'observed_frames_per_second':len(frames)/seconds,
            'performance':{'probe_seconds':probe_seconds,'decode_seconds':decode_seconds,'analysis_tracking_seconds':analysis_seconds,
                           'scope':'measured host run; includes bounded snapshot and verification in wall time'},
            'resources':{'decoded_png_bytes':decoded_bytes,'maximum_frames':plan['maximum_frames'],
                         'maximum_decoded_grid':[300,400],'decoder_per_allocation_bytes':67108864,
                         'total_native_rss_bounded':False},
            'limitations':['Constant-velocity IoU tracker; crossing and long occlusions can switch identities.',
                           'Track labels are geometric hypotheses, not verified semantic identities.',
                           'Processes at most the requested initial duration; no live camera or streaming claim.',
                           'Native decoder total RSS is not bounded; this is not a decoder sandbox.']}
