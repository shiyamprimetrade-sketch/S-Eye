#!/usr/bin/env python3
"""Reproducible generated experiments, not representative photographic validation."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
from PIL import Image, ImageDraw, ImageOps
from seye.core.storage import atomic_json, checksum
from seye.detection.annotations import evaluate_annotations
from seye.learning.dataset import grouped_classification_split, train, train_linear, load_samples
from seye.learning.prototypes import save_model, load_model, predict, UNKNOWN
from seye.memory.store import Memory
from seye.recognition.features import FEATURE_VERSION
from seye.video.ingestion import analyze_video


def generated_dataset(root, count=12):
    rng = random.Random(20261112)
    rows = []
    for label in ('circle', 'quadrilateral', 'triangle', UNKNOWN):
        for index in range(count if label != UNKNOWN else 6):
            image = Image.new('RGB', (180, 180), tuple(rng.randint(210, 255) for _ in range(3)))
            layer = Image.new('RGBA', (120, 120)); draw = ImageDraw.Draw(layer)
            ink = tuple(rng.randint(0, 70) for _ in range(3)) + (255,)
            width = rng.randint(4, 9)
            if label == 'circle':
                draw.ellipse((20, 20, 100, 100), outline=ink, width=width)
            elif label == 'quadrilateral':
                draw.rectangle((20, 20, 100, 100), outline=ink, width=width)
            elif label == 'triangle':
                draw.polygon([(60, 12), (15, 105), (105, 105)], outline=ink, width=width)
            else:
                draw.line((10, 15, 110, 105), fill=ink, width=width)
                draw.line((110, 15, 10, 105), fill=ink, width=width)
            layer = layer.rotate(rng.randint(-25, 25), resample=Image.Resampling.BICUBIC)
            image.paste(layer, (rng.randint(0, 60), rng.randint(0, 60)), layer)
            path = root / f'{label}-{index}.png'; image.save(path)
            rows.append({'id': path.stem, 'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'label': label, 'source_kind': 'synthetic', 'annotation_status': 'generator',
                         'capture_group': path.stem})
    return grouped_classification_split({'schema_version': 1, 'images': rows}, root)


def annotation_benchmark(root):
    rows = []
    for index, ink in enumerate((0, 240)):
        image = Image.new('RGB', (300, 300), 'white'); draw = ImageDraw.Draw(image)
        draw.ellipse((30, 40, 100, 110), outline=(ink,)*3, width=5)
        draw.rectangle((170, 40, 240, 110), outline=(ink,)*3, width=5)
        path = root / f'instances-{index}.png'; image.save(path)
        mask = image.convert('L').point(lambda p: 255 if p < 255 else 0)
        mask_path = root / f'mask-{index}.png'; mask.save(mask_path)
        rows.append({'id': str(index), 'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'capture_group': str(index), 'annotation_status': 'generator', 'annotator': 'benchmark generator',
                     'source_kind': 'synthetic', 'instances': [{'id': 'c', 'class': 'circle', 'box': [30, 40, 101, 111]},
                                                               {'id': 'q', 'class': 'quadrilateral', 'box': [170, 40, 241, 111]}],
                     'mask': mask_path.name, 'mask_sha256': hashlib.sha256(mask_path.read_bytes()).hexdigest(), 'mask_scope': 'dark_strokes'})
    manifest = root / 'instances.json'; atomic_json(manifest, {'schema_version': 1, 'coordinate_space': 'exif_oriented_source', 'images': rows})
    return {mode: evaluate_annotations(manifest, mode) for mode in ('baseline', 'adaptive')}


def video_benchmark(root):
    for frame in range(6):
        image = Image.new('RGB', (300, 240), 'white')
        ImageDraw.Draw(image).ellipse((30 + frame*5, 70, 90 + frame*5, 130), outline='black', width=5)
        image.save(root / f'frame-{frame:03d}.png')
    path = root / 'controlled.mp4'
    process = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-framerate', '2', '-i', str(root / 'frame-%03d.png'),
                              '-c:v', 'mpeg4', '-q:v', '2', str(path)], capture_output=True, text=True, timeout=30)
    if process.returncode:
        raise RuntimeError('Generated MP4 encoding failed: ' + process.stderr)
    result = analyze_video(path, root, fps=2, max_seconds=3)
    previous = None; switches = 0; misses = 0
    for frame in result['frames']:
        visible = frame['visible']
        if len(visible) != 1:
            misses += 1
            continue
        current = visible[0]['track_id']
        switches += previous is not None and previous != current
        previous = current
    result['controlled_tracking_metrics'] = {'expected_objects_per_frame': 1, 'identity_switches': switches,
                                             'frames_without_exactly_one_track': misses,
                                             'scope': 'one generated moving circle, no crossing or occlusion in this clip'}
    return result


def benchmark():
    with tempfile.TemporaryDirectory(prefix='seye_system_') as directory:
        root = Path(directory)
        data = generated_dataset(root); manifest = root / 'classification.json'; atomic_json(manifest, data)
        model, learning = train(manifest); save_model(root / 'model.json', model)
        from seye.detection.analysis import analyze
        restored = load_model(root / 'model.json')
        linear_model, linear_learning = train_linear(manifest)
        save_model(root / 'linear-model.json', linear_model)
        linear_restored = load_model(root / 'linear-model.json')
        _, samples = load_samples(manifest)
        fixed_baseline = []
        for row in samples:
            if row['split'] == 'test':
                analysis, _ = analyze(root / row['path'])
                labels = [obj['class'] for obj in analysis['objects']]
                fixed_baseline.append({'id': row['id'], 'expected': row['label'],
                                       'predicted': labels[0] if len(labels) == 1 else UNKNOWN})
        fixed_baseline_report = {'samples': len(fixed_baseline), 'correct': sum(r['expected'] == r['predicted'] for r in fixed_baseline), 'results': fixed_baseline}
        restore_equal = all(predict(model, r['features']) == predict(restored, r['features']) for r in samples)
        memory = Memory(root / 'memory.sqlite3')
        try:
            for row in samples:
                if row['split'] == 'train':
                    memory.put({'schema_version': 1, 'features': row['features'], 'feature_version': FEATURE_VERSION,
                                'provenance': {'source_sha256': row['sha256'], 'label': row['label'], 'id': row['id']}})
            queries = [r for r in samples if r['split'] == 'test' and r['label'] != UNKNOWN]
            correct = sum(memory.search(r['features'], 1)[0]['provenance']['label'] == r['label'] for r in queries)
            memory.export(root / 'memory.json')
            other = Memory(root / 'restored.sqlite3')
            try:
                restored_memory = other.import_file(root / 'memory.json')
            finally:
                other.close()
            retrieval = {'queries': len(queries), 'top1_same_generator_category': correct,
                         'integrity': memory.verify(), 'restored_integrity': restored_memory,
                         'sqlite_file_bytes': (root / 'memory.sqlite3').stat().st_size}
        finally:
            memory.close()
        annotations = annotation_benchmark(root)
        video = video_benchmark(root)
        tracemalloc.start(); start = time.perf_counter()
        for row in samples[:10]:
            predict(model, row['features'])
        seconds = time.perf_counter() - start; _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        return {'schema_version': 1, 'scope': 'controlled_generated_system_experiments', 'representative_validation': False,
                'runtime': {'python': platform.python_version(), 'system': platform.system(), 'machine': platform.machine()},
                'classification_manifest': data, 'fitted_model': model, 'learning': learning, 'linear_model': linear_model, 'linear_learning': linear_learning,
                'linear_checkpoint_prediction_equivalence': all(predict(linear_model, r['features']) == predict(linear_restored, r['features']) for r in samples), 'fixed_geometry_baseline': fixed_baseline_report, 'checkpoint_prediction_equivalence': restore_equal,
                'memory': retrieval, 'localization': annotations, 'video': video,
                'descriptor_inference_performance': {'queries': min(10, len(samples)), 'wall_seconds': seconds,
                                                      'python_tracemalloc_peak_bytes': peak,
                                                      'scope': 'descriptor classification only; excludes decode/extraction; one host observation'},
                'code_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src/seye').rglob('*.py'))},
                'limitations': ['All training/evaluation imagery is generated; no broad semantic/photo validation.',
                                'Prototype fitting is independent feature-based learning, not neural training.',
                                'Unknown rejection measured only on generated cross shapes.',
                                'Video benchmark is one simple MP4, not representative tracking quality.',
                                'Actual Android/Windows performance and main-S deployment remain unverified.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); result = benchmark(); atomic_json(args.output, result)
    print(json.dumps({'test': {k:v for k,v in result['learning']['test'].items() if k!='results'},
                      'linear_test': {k:v for k,v in result['linear_learning']['test'].items() if k not in ('results','confusion')},
                      'memory': result['memory'], 'tracking': result['video']['controlled_tracking_metrics']}, indent=2))
