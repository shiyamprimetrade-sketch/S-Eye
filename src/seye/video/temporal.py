"""Explicit resampling clocks and frame-local geometry contracts.

These are sample-grid times, never original video presentation timestamps.
"""
import math
from seye.detection.metrics import valid_box


def finite(value, name, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} must be finite and >= {minimum}')
    return value


def sampling_plan(fps=2, seconds=4):
    if type(fps) is not int or not 1 <= fps <= 10:
        raise ValueError('fps must be an integer in 1..10')
    if type(seconds) is not int or not 1 <= seconds <= 30:
        raise ValueError('seconds must be an integer in 1..30')
    return {'fps': fps, 'maximum_frames': fps * seconds,
            'timestamps': [index / fps for index in range(fps * seconds)],
            'timestamp_scope': 'resampled constant-rate grid; not original presentation timestamps'}


def frame_contract(detections, timestamp, size, previous_timestamp=None, maximum=64):
    """Validate the complete frame before any state can change; copy caller data."""
    finite(timestamp, 'timestamp')
    if timestamp>1_000_000_000:raise ValueError('Sampling time exceeds supported bound')
    if previous_timestamp is not None:finite(previous_timestamp,'previous_timestamp')
    if previous_timestamp is not None and timestamp-previous_timestamp < 1e-6:
        raise ValueError('Sample times must increase by at least one microsecond')
    if not isinstance(size, (list, tuple)) or len(size) != 2 or any(type(n) is not int or not 1 <= n <= 4096 for n in size):
        raise ValueError('Two integer frame dimensions in 1..4096 required')
    if not isinstance(detections, list) or len(detections) > maximum:
        raise ValueError(f'At most {maximum} explicit detections allowed')
    clean = []
    for row in detections:
        if not isinstance(row, dict):
            raise ValueError('Detection must be an object')
        box, label = row.get('box'), row.get('class')
        valid_box(box)
        if box[0] < 0 or box[1] < 0 or box[2] > size[0] or box[3] > size[1]:
            raise ValueError('Box outside decoded-frame grid')
        if not isinstance(label, str) or not 1 <= len(label) <= 128:
            raise ValueError('Bounded geometric class required')
        clean.append({'class': label, 'box': list(box)})
    return clean
