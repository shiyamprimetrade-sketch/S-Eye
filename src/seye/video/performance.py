"""Per-frame tracking timings; excludes decode, segmentation and host interaction."""
import math
import time
from seye.video.continuity import ContinuityTracker
from seye.video.temporal import frame_contract


def latency_report(durations, total_seconds):
    if not isinstance(durations,list) or not 1<=len(durations)<=300:
        raise ValueError('1..300 durations required')
    values=durations+[total_seconds]
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values):raise ValueError('Finite nonnegative timings required')
    ordered=sorted(durations)
    percentile=lambda q:ordered[max(0,math.ceil(q*len(ordered))-1)]
    return {'sampled_frames':len(durations),'tracking_wall_seconds':total_seconds,
            'tracking_frames_per_second':len(durations)/total_seconds if total_seconds else None,
            'frame_latency_seconds':{'minimum':ordered[0],'p50':percentile(.5),'p95':percentile(.95),'maximum':ordered[-1]},
            'scope':'box association only; excludes decode, segmentation, disk, and live capture',
            'portable_speed_claim':False}


def track_samples(samples, config=None):
    if not isinstance(samples,list) or not 1<=len(samples)<=300:raise ValueError('1..300 explicit samples required')
    previous=None
    for sample in samples:
        if not isinstance(sample,dict):raise ValueError('Sample object required')
        frame_contract(sample.get('detections'),sample.get('timestamp'),sample.get('source_size'),previous)
        previous=sample['timestamp']
    tracker=ContinuityTracker(**({} if config is None else config))
    frames=[];durations=[];start=time.perf_counter()
    for sample in samples:
        before=time.perf_counter()
        frames.append(tracker.update(sample['detections'],sample['timestamp'],sample['source_size'],sample.get('discontinuity',False)))
        durations.append(time.perf_counter()-before)
    elapsed=time.perf_counter()-start
    return {'frames':frames,'performance':latency_report(durations,elapsed),
            'candidate_edges':sum(len(frame['candidate_edges']) for frame in frames)}
