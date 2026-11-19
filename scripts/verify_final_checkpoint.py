#!/usr/bin/env python3
"""Combine fresh generated measurements and check historical behavior."""
import argparse
from importlib.metadata import version
import math
from pathlib import Path
import platform
from statistics import median
import tempfile
from time import perf_counter

from seye import __version__
from seye.core.storage import atomic_json, read_json
from seye.interface.observer import observe

from benchmark_stage151_160 import fixture, stage158
from benchmark_tracking_validation import run as tracking_run
from compare_learning_batch import run as recognition_run


ROOT = Path(__file__).resolve().parents[1]


def code_inventory():
    from hashlib import sha256
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted((ROOT / 'src/seye').rglob('*.py'))}


def performance():
    with tempfile.TemporaryDirectory() as directory:
        image = fixture(directory)
        options = {'region_proposals': True, 'region_mode': 'refined'}
        expected = observe(image, **options)
        elapsed_ms = []
        for _ in range(20):
            start = perf_counter()
            actual = observe(image, **options)
            elapsed_ms.append((perf_counter() - start) * 1000)
            if actual != expected:
                raise ValueError('Observation changed across repeated identical inputs')
    elapsed_ms.sort()
    return {'samples': len(elapsed_ms), 'source_size': [160, 120],
            'p50_ms': median(elapsed_ms), 'p95_ms': elapsed_ms[math.ceil(.95 * len(elapsed_ms)) - 1],
            'max_ms': elapsed_ms[-1], 'runtime': platform.python_version(), 'host': platform.system(),
            'scope': 'warm generated PNG read, hash, decode and refined region proposals; no device inference'}


def verify(experiment):
    inventory = code_inventory()
    normalized = {key.replace('\\', '/'): value for key, value in experiment['code_sha256'].items()}
    if normalized != inventory:
        raise ValueError('System experiment does not match the current source files')
    historical = read_json(ROOT / 'benchmarks/independent_system.json')
    classification_keys = ('samples', 'known_samples', 'known_correct', 'unknown_samples', 'unknown_rejected')
    for name in ('learning', 'linear_learning'):
        before = historical[name]['test']
        after = experiment[name]['test']
        for key in classification_keys:
            if key in before and after.get(key) != before[key]:
                raise ValueError(f'Historical {name} generated result changed: {key}')
    recognition = recognition_run()['methods']
    recognition_baseline = read_json(ROOT / 'benchmarks/stage118_experiment.json')['result']['methods']
    glyph_counts = {name: {key: recognition[name][key] for key in keys}
                    for name, keys in recognition_baseline.items()}
    if glyph_counts != recognition_baseline:
        raise ValueError('Historical glyph recognition counts changed')
    checkpoint_passed = (experiment['checkpoint_prediction_equivalence']
                         and experiment['linear_checkpoint_prediction_equivalence'])
    if not checkpoint_passed:
        raise ValueError('Restored model predictions differ')
    retrieval = experiment['memory']
    for key in ('queries', 'top1_same_generator_category', 'integrity', 'restored_integrity'):
        if retrieval[key] != historical['memory'][key]:
            raise ValueError(f'Historical memory result changed: {key}')
    memory = stage158()
    if not memory['passed']:
        raise ValueError('Memory backup and restored index check failed')
    tracking = tracking_run()
    baseline = read_json(ROOT / 'benchmarks/stage149_experiment.json')
    if tracking['totals'] != baseline['totals']:
        raise ValueError('Historical tracking stress totals changed')
    video = experiment['video']
    metrics = video['controlled_tracking_metrics']
    if video['processed_frames'] != 6 or metrics['identity_switches'] or metrics['frames_without_exactly_one_track']:
        raise ValueError('Controlled prerecorded video failed')
    installed_version = version('seye-independent')
    if installed_version != __version__:
        raise ValueError('Installed package version does not match source')
    return {
        'schema_version': 1, 'source_sha256': inventory, 'scope': 'controlled generated development checkpoint',
        'historical_counts_preserved': True, 'model_roundtrip': checkpoint_passed,
        'independent_recognition': {name: {key: experiment[name]['test'][key] for key in classification_keys
                                          if key in experiment[name]['test']} for name in ('learning', 'linear_learning')},
        'glyph_recognition': glyph_counts,
        'visual_memory': {'queries': experiment['memory']['queries'],
                          'top1_same_generator_category': experiment['memory']['top1_same_generator_category'],
                          'restored_observations': memory['recovered_observations'],
                          'storage_backup_bytes': memory['backup']['snapshot_bytes']},
        'video': {'mp4_frames': video['processed_frames'], 'single_object_metrics': metrics,
                  'association_stress_sequences': tracking['generated_sequences'], 'stress_totals': tracking['totals']},
        'performance': performance(), 'installed_version': installed_version,
        'representative_validation': False, 'v1_release': False,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    atomic_json(args.output, verify(read_json(args.experiment)))
