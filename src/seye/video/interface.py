"""Bounded prerecorded interface observations; timestamps are a sampling grid."""
import hashlib
from pathlib import Path
import tempfile
from seye.video.ingestion import analyze_video


def observe_video(path, allowed_root, fps=2, max_seconds=4, tracking_mode="legacy"):
    """Reuse the checked local decoder; preserve its geometric tracking evidence.

    This adapter deliberately limits output and makes the coordinate/timing
    contract explicit. It does not infer UI semantics or original frame PTS.
    """
    if type(fps) is not int or not 1 <= fps <= 4 or type(max_seconds) is not int or not 1 <= max_seconds <= 6:
        raise ValueError('Interface sampling requires fps 1..4 and duration 1..6 seconds')
    if tracking_mode not in ('legacy','conservative'):raise ValueError('Unsupported tracking mode')
    report = analyze_video(path, allowed_root, fps=fps, max_seconds=max_seconds, temporal_details=tracking_mode=='conservative')
    if tracking_mode=='conservative':
        from seye.video.sequence import observe_sequence
        from seye.video.summary import summarize
        samples=[{'detections':[{'class':r['class'],'box':r['box']} for r in f['visible']],
                  'timestamp':f['timestamp'],'source_size':f['source_size']} for f in report['frames']]
        temporal=observe_sequence(samples,report['source_sha256'])
        for old,new in zip(report['frames'],temporal['frames']):
            new['decoded_frame_sha256']=old['decoded_frame_sha256']
            new['sample_index']=old['sample_index']
        report['frames']=temporal['frames']
        report['track_summaries']=summarize(temporal['frames'],report['source_sha256'])['tracks']
        report['temporal_checkpoint']=temporal['checkpoint']
        report['temporal_performance']=temporal['performance']
        report['tracking_limitations']=['Conservative ambiguity abstention can increase misses and identity switches.',
                                         'Geometric classification and merged-region detection failures remain.']
    return dict(report, tracking_mode=tracking_mode, observation_kind='prerecorded_geometric_frames',
                coordinate_scope='decoded frames scaled to fit 300x400; not original video pixels',
                semantic_interface_identity=None, automatic_action_authorized=False,
                requested_max_frames=fps * max_seconds)


def generated_probe():
    """Encode and decode an actual local clip; returns execution evidence only."""
    import subprocess
    from PIL import Image, ImageDraw
    with tempfile.TemporaryDirectory(prefix='seye_clip_probe_') as directory:
        root = Path(directory)
        for i in range(4):
            image = Image.new('RGB', (160, 120), 'white')
            ImageDraw.Draw(image).rectangle((20 + i*3, 20, 60 + i*3, 50), fill='black')
            image.save(root / f'{i:03d}.png')
        clip = root / 'clip.mp4'
        subprocess.run(['ffmpeg','-v','error','-nostdin','-threads','1','-framerate','2','-i',str(root/'%03d.png'),'-c:v','mpeg4','-pix_fmt','yuv420p',str(clip)],check=True,timeout=20,capture_output=True)
        digest = hashlib.sha256(clip.read_bytes()).hexdigest()
        report = observe_video(clip, root, fps=2, max_seconds=2)
        return {'frames':report['processed_frames'], 'timestamps':[f['timestamp'] for f in report['frames']],
                'source_preserved':report['source_sha256']==digest==hashlib.sha256(clip.read_bytes()).hexdigest(),
                'automatic_action_authorized':report['automatic_action_authorized'],
                'timestamp_scope':report['timestamp_scope']}
