#!/usr/bin/env python3
"""Stage 85: evidence-preserving evaluation of the unchanged camera pipeline.

Class presence only: no localization, instance counting or object recognition claim.
Transformations are simulated perturbations, never independent camera captures.
"""
import argparse
import hashlib
import io
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import PIL
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent
SCRIPTS = ('local_contrast.py', 'group_shapes.py', 'filter_regions.py',
           'classify_camera_v2.py')
OUTPUTS = ('local_contrast_mask.png', 'grouped_shapes.png', 'filtered_shapes.png')
CLASSES = {'circle', 'quadrilateral', 'triangle'}
VARIANTS = ('original', 'dim', 'bright', 'low_contrast', 'rotate_15',
            'rotate_minus15', 'affine_shear', 'jpeg_50')
PATTERN = re.compile(r'^Region\s+\d+:\s+(.+?),\s*corners=\d+,\s*hull_vertices=\d+\s*$', re.M)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(label):
    """Explicit shared taxonomy, including square/rectangle Stage 84 omissions."""
    return {'Circle-like': 'circle', 'Triangle': 'triangle',
            'Square-like': 'quadrilateral', 'Rectangle-like': 'quadrilateral',
            'Ambiguous quadrilateral': 'quadrilateral', 'Unknown': 'unknown'}.get(label, 'unknown')


def class_metrics(expected, predicted):
    """Set metrics: repeated instances must not change class-presence precision."""
    expected, predicted = set(expected), set(predicted)
    tp = len(expected & predicted)
    fp, fn = len(predicted - expected), len(expected - predicted)
    return {'tp': tp, 'fp': fp, 'fn': fn,
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None,
            'exact_match': expected == predicted}


def load_manifest(path, check_splits=True):
    path = Path(path).resolve()
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('images'), list) or not data['images']:
        raise ValueError('Expected schema_version=1 and a nonempty images list')
    seen_ids, seen_hashes = set(), set()
    for row in data['images']:
        if not isinstance(row, dict):
            raise ValueError('Each image must be an object')
        if not isinstance(row.get('id'), str) or not row['id'] or row['id'] in seen_ids:
            raise ValueError('Image IDs must be nonempty and unique')
        seen_ids.add(row['id'])
        if not isinstance(row.get('path'), str):
            raise ValueError('Image path required')
        photo = (path.parent / row['path']).resolve()
        if not photo.is_relative_to(path.parent):
            raise ValueError('Images must reside inside the manifest directory')
        if photo.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
            raise ValueError('Unsupported image extension')
        actual = digest(photo)
        if row.get('sha256') != actual:
            raise ValueError(f"Source hash mismatch: {row['id']}")
        if actual in seen_hashes:
            raise ValueError('Duplicate source bytes cannot count as independent images')
        seen_hashes.add(actual)
        labels = row.get('expected_classes')
        if not isinstance(labels, list) or any(not isinstance(x, str) or x not in CLASSES for x in labels) or len(set(labels)) != len(labels):
            raise ValueError('Expected unique labels from circle, quadrilateral, triangle')
        if type(row.get('human_confirmed')) is not bool:
            raise ValueError('human_confirmed must be a boolean')
        if row.get('source_kind') not in ('photograph', 'synthetic'):
            raise ValueError('source_kind must be photograph or synthetic')
        for key in ('capture_group', 'lighting', 'camera_angle', 'annotation_source'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f'{key} must be a nonempty string')
        if row['source_kind'] == 'synthetic' and row['human_confirmed']:
            raise ValueError('Synthetic labels use generator truth, not human photo confirmation')
        with Image.open(photo) as image:
            image.verify()
    if check_splits and any('split' in row for row in data['images']):
        from dataset_tools import validate_splits
        validate_splits(data['images'], path.parent)
    return data


def transform(image, variant):
    image = ImageOps.exif_transpose(image).convert('RGB')
    if variant == 'original':
        return image.copy()
    if variant in ('dim', 'bright'):
        return ImageEnhance.Brightness(image).enhance(0.55 if variant == 'dim' else 1.3)
    if variant == 'low_contrast':
        return ImageEnhance.Contrast(image).enhance(0.45)
    if variant.startswith('rotate_'):
        angle = -15 if variant == 'rotate_minus15' else 15
        return image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor='white')
    if variant == 'affine_shear':
        # An affine image warp is only an angle stress proxy, not a physical camera model.
        return image.transform(image.size, Image.Transform.AFFINE,
                               (1, 0.15, -0.075 * image.height, 0, 1, 0),
                               resample=Image.Resampling.BICUBIC, fillcolor='white')
    if variant == 'jpeg_50':
        stream = io.BytesIO()
        image.save(stream, format='JPEG', quality=50)
        stream.seek(0)
        with Image.open(stream) as compressed:
            return compressed.convert('RGB')
    raise ValueError(f'Unknown variant: {variant}')


def run_pipeline(photo):
    """Execute all four existing scripts in a fresh directory, without memory writes."""
    with tempfile.TemporaryDirectory(prefix='s_eye_stage85_') as directory:
        work = Path(directory)
        source = work / ('input' + Path(photo).suffix.lower())
        shutil.copy2(photo, source)
        source_hash = digest(source)
        steps = []
        for script in SCRIPTS:
            shutil.copy2(ROOT / script, work / script)
            command = [sys.executable, str(work / script)]
            if script == SCRIPTS[0]:
                command += ['--image', str(source)]
            result = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=120)
            steps.append({'script': script, 'returncode': result.returncode,
                          'stdout': result.stdout, 'stderr': result.stderr})
            if result.returncode:
                raise RuntimeError(f'{script} failed: {result.stderr[-1000:]}')
        if f'Source SHA-256: {source_hash}' not in steps[0]['stdout'] or digest(source) != source_hash:
            raise RuntimeError('Pipeline source provenance mismatch')
        labels = PATTERN.findall(steps[-1]['stdout'])
        count = re.search(r'^Accepted regions: (\d+)$', steps[-1]['stdout'], re.M)
        if count is None or int(count.group(1)) != len(labels):
            raise RuntimeError('Classifier output contract mismatch')
        return {'labels': labels, 'classes': sorted(set(map(normalize, labels))),
                'artifacts': {name: digest(work / name) for name in OUTPUTS}, 'steps': steps}


def evaluate(manifest, variants=VARIANTS, split=None):
    manifest = Path(manifest).resolve()
    data = load_manifest(manifest)  # Validate the entire dataset before execution.
    if not variants or len(set(variants)) != len(variants) or any(v not in VARIANTS for v in variants):
        raise ValueError('Expected unique supported variants')
    if split is not None:
        if split not in ('train', 'validation', 'test'):
            raise ValueError('Unsupported split')
        selected = [row for row in data['images'] if row.get('split') == split]
        if not selected:
            raise ValueError('Requested split has no images')
    else:
        selected = data['images']
    results = []
    with tempfile.TemporaryDirectory(prefix='s_eye_variants_') as directory:
        for row in selected:
            source = manifest.parent / row['path']
            for variant in variants:
                if variant == 'original':
                    candidate = source  # Preserve original JPEG/EXIF behavior.
                else:
                    candidate = Path(directory) / 'variant.png'
                    with Image.open(source) as image:
                        transform(image, variant).save(candidate)
                record = {key: row[key] for key in ('id', 'source_kind', 'human_confirmed',
                          'capture_group', 'lighting', 'camera_angle', 'annotation_source', 'expected_classes')}
                record['split'] = row.get('split', 'unsplit')
                record.update(variant=variant, source_sha256=row['sha256'], input_sha256=digest(candidate))
                try:
                    record['prediction'] = run_pipeline(candidate)
                    record['metrics'] = class_metrics(row['expected_classes'], record['prediction']['classes'])
                    record['pipeline_success'] = True
                except (RuntimeError, subprocess.TimeoutExpired, OSError) as error:
                    record.update(pipeline_success=False, error=str(error))
                results.append(record)
            if digest(source) != row['sha256']:
                raise RuntimeError('Source changed during evaluation')
    # Keep source/annotation/split/condition partitions separate, including failures.
    from dataset_tools import diagnostics
    details = diagnostics(results)
    summaries = [{key: row[key] for key in ('source_kind', 'human_confirmed', 'split', 'variant',
                 'pipeline_failures', 'exact_matches')} | {'cases': row['attempted_cases']}
                 for row in details['summaries']]
    return {'schema_version': 2, 'stage': 86, 'evaluation_type': 'class_presence',
            'manifest_sha256': digest(manifest),
            'runtime': {'python': platform.python_version(), 'pillow': PIL.__version__},
            'pipeline_sha256': {name: digest(ROOT / name) for name in SCRIPTS},
            'evaluator_sha256': digest(ROOT / 'generalization.py'),
            'support_sha256': {name: digest(ROOT / name) for name in (
                'dataset_tools.py', 'src/seye/core/datasets.py', 'src/seye/core/evaluation.py')},
            'distinct_sources': len(selected),
            'manifest_sources': len(data['images']), 'selected_split': split,
            'recognition_validation_status': 'not_established',
            'data_scope': 'synthetic_only' if all(r['source_kind'] == 'synthetic' for r in selected) else 'photographs_present',
            'split_provenance': data.get('split_provenance'),
            'diagnostics': details,
            'confirmed_photographs': sum(r['source_kind'] == 'photograph' and r['human_confirmed'] for r in selected),
            'localization_evaluated': False,
            'limitations': ['Perturbations of one image are correlated, not independent captures.',
                            'Class presence does not evaluate localization or instance counts.',
                            'Synthetic results do not establish photographic generalization.',
                            'Circle-like and polygon labels are geometric hypotheses, not object identities.'],
            'summary': summaries, 'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--split', choices=('train', 'validation', 'test'))
    parser.add_argument('--variants', nargs='+', choices=VARIANTS, default=VARIANTS)
    args = parser.parse_args()
    try:
        # Avoid destroying inputs or existing evidence through an accidental output path.
        if args.output.exists():
            raise ValueError('Output already exists; choose a new report path')
        report = evaluate(args.manifest, tuple(args.variants), args.split)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    except (ValueError, OSError) as error:
        parser.exit(2, f'Invalid evaluation: {error}\n')
    print(json.dumps({key: report[key] for key in ('distinct_sources', 'confirmed_photographs', 'summary')}, indent=2))
    return 0 if all(r['pipeline_success'] for r in report['results']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
