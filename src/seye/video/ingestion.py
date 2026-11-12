"""Local prerecorded-video decoding via optional FFmpeg; no external recognition models."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from seye.detection.analysis import analyze
from seye.video.tracking import Tracker


def analyze_video(path, allowed_root, fps=2, max_seconds=30, mode='baseline'):
    path, allowed_root = Path(path).resolve(), Path(allowed_root).resolve()
    if not path.is_relative_to(allowed_root) or not path.is_file() or path.suffix.lower() not in ('.mp4', '.mov', '.mkv', '.avi'):
        raise ValueError('Permitted local video file required')
    if path.stat().st_size > 128 * 1024 * 1024:
        raise ValueError('Video exceeds 128 MiB')
    if type(fps) is not int or not 1 <= fps <= 10 or type(max_seconds) is not int or not 1 <= max_seconds <= 30:
        raise ValueError('Video sampling limits exceeded')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('Optional local ffmpeg/ffprobe executables required')
    probe = subprocess.run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe', '-select_streams', 'v:0',
                            '-show_entries', 'stream=width,height', '-of', 'json', str(path)],
                           capture_output=True, text=True, timeout=10)
    if probe.returncode:
        raise ValueError('Video metadata decode failed')
    streams = json.loads(probe.stdout).get('streams', [])
    if not streams or streams[0]['width'] * streams[0]['height'] > 20_000_000:
        raise ValueError('Unsupported video dimensions')
    initial_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    start = time.perf_counter(); tracker = Tracker(); frames = []
    with tempfile.TemporaryDirectory(prefix='seye_video_') as directory:
        result = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-protocol_whitelist', 'file,pipe',
                                 '-threads', '1', '-i', str(path), '-t', str(max_seconds), '-vf',
                                 f'fps={fps},scale=300:400:force_original_aspect_ratio=decrease',
                                 '-frames:v', str(fps * max_seconds), str(Path(directory) / '%06d.png')],
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise ValueError('Video frame decode failed')
        for index, frame in enumerate(sorted(Path(directory).glob('*.png'))):
            report, _ = analyze(frame, mode)
            detections = [{'class': row['class'], 'box': row['source_box']} for row in report['objects']]
            frames.append(tracker.update(detections, index / fps))
    if not frames:
        raise ValueError('No video frames decoded')
    seconds = time.perf_counter() - start
    if hashlib.sha256(path.read_bytes()).hexdigest() != initial_hash:
        raise ValueError('Video source changed during decode')
    history = {}
    for frame in frames:
        for obj in frame['visible']:
            history.setdefault(obj['track_id'], []).append(frame['timestamp'])
    summaries = [{'track_id': identifier, 'first_seen': times[0], 'last_seen': times[-1], 'sampled_observations': len(times)}
                 for identifier, times in sorted(history.items())]
    return {'schema_version': 1, 'source_sha256': initial_hash, 'track_summaries': summaries,
            'sample_fps': fps, 'timestamp_scope': 'resampled constant-rate grid; not original presentation timestamps',
            'frames': frames, 'processed_frames': len(frames), 'wall_seconds': seconds,
            'observed_frames_per_second': len(frames) / seconds,
            'limitations': ['Constant-velocity IoU tracker; crossing and long occlusions can switch identities.',
                            'Track labels are geometric hypotheses, not verified semantic identities.',
                            'Processes at most the requested initial duration; no live camera or streaming claim.']}
