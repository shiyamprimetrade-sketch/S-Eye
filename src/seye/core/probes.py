"""Unlabelled real-input probes: execution and repeatability, never accuracy."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile
import time

import platform
import PIL
from PIL import Image, ImageEnhance
from seye.detection.analysis import analyze
from seye.image.ingestion import load_image

VARIANTS = ('original', 'dim', 'rotate15')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_manifest(manifest):
    manifest = Path(manifest).resolve()
    data = json.loads(manifest.read_text())
    if not isinstance(data, dict) or data.get('schema_version') != 1 or data.get('annotation_status') != 'unlabelled':
        raise ValueError('Expected an unlabelled schema-1 probe manifest')
    rows = data.get('images')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100:
        raise ValueError('Probe requires 1..100 images')
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'] or row['id'] in seen:
            raise ValueError('Unique nonempty image IDs required')
        seen.add(row['id'])
        if row.get('source_kind') not in ('photograph', 'screenshot'):
            raise ValueError('Specify photograph or screenshot; these sources must not be conflated')
        if any(key in row for key in ('expected_classes', 'ground_truth', 'human_confirmed')):
            raise ValueError('Unlabelled probes cannot assert ground truth or annotation confirmation')
        if not isinstance(row.get('path'), str):
            raise ValueError('Image path required')
        path = (manifest.parent / row['path']).resolve()
        # Validate all inputs before any inference or file writing.
        _, source = load_image(path, allowed_root=manifest.parent)
        if row.get('sha256') != source['sha256']:
            raise ValueError(f"Source hash mismatch: {row['id']}")
    return data


def probe(manifest, variants=VARIANTS, repeats=2, overlay_directory=None):
    manifest = Path(manifest).resolve()
    data = validate_manifest(manifest)
    if 'original' not in variants or len(set(variants)) != len(variants) or any(v not in VARIANTS for v in variants):
        raise ValueError('Unique supported perturbation variants required')
    if type(repeats) is not int or not 1 <= repeats <= 5:
        raise ValueError('Repeat count must be 1..5')
    if overlay_directory is not None:
        overlay_directory = Path(overlay_directory)
        overlay_directory.mkdir(parents=True, mode=0o700, exist_ok=False)
    cases = []
    with tempfile.TemporaryDirectory(prefix='seye_probes_') as directory:
        for index, row in enumerate(data['images']):
            source = manifest.parent / row['path']
            image, _ = load_image(source, allowed_root=manifest.parent)
            for variant in variants:
                if variant == 'original':
                    candidate = source
                else:
                    changed = (ImageEnhance.Brightness(image).enhance(.55) if variant == 'dim' else
                               image.rotate(15, resample=Image.Resampling.BICUBIC, expand=True, fillcolor='white'))
                    candidate = Path(directory) / 'variant.png'
                    changed.save(candidate)
                for mode in ('baseline', 'adaptive'):
                    for repetition in range(repeats if variant == 'original' else 1):
                        record = {'id': row['id'], 'source_kind': row['source_kind'],
                                  'source_sha256': row['sha256'], 'variant': variant,
                                  'mode': mode, 'repetition': repetition,
                                  'input_sha256': sha256(candidate)}
                        start = time.perf_counter()
                        try:
                            report, artifacts = analyze(candidate, mode)
                            record.update(pipeline_success=True, analysis=report)
                            record['prediction_sha256'] = hashlib.sha256(json.dumps(
                                report['objects'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                            record['mask_pixel_sha256'] = hashlib.sha256(artifacts['mask'].tobytes()).hexdigest()
                            if overlay_directory is not None and variant == 'original' and repetition == 0:
                                from PIL import ImageDraw
                                preview = artifacts['source'].copy()
                                draw = ImageDraw.Draw(preview)
                                for obj in report['objects']:
                                    box = obj['source_box']
                                    draw.rectangle(box, outline='red', width=3)
                                    draw.text((box[0], max(0, box[1] - 12)), f"{obj['id']}: {obj['label']}", fill='red')
                                preview.thumbnail((600, 800))
                                # Numeric names prevent untrusted IDs from becoming filesystem paths.
                                preview.save(overlay_directory / f'{index:03d}_{mode}.jpg')
                        except (ValueError, OSError) as error:
                            record.update(pipeline_success=False, error=str(error))
                        record['wall_seconds'] = time.perf_counter() - start
                        cases.append(record)
            if sha256(source) != row['sha256']:
                raise RuntimeError('Input changed during probing')
    stability, summary = [], []
    for row in data['images']:
        for mode in ('baseline', 'adaptive'):
            originals = [r for r in cases if r['id'] == row['id'] and r['mode'] == mode and r['variant'] == 'original']
            complete = all(r['pipeline_success'] for r in originals)
            stability.append({'id': row['id'], 'mode': mode, 'repeats': len(originals),
                              'all_completed': complete,
                              'stable_predictions': len({r.get('prediction_sha256') for r in originals}) == 1 if complete and len(originals) >= 2 else None,
                              'stable_mask_pixels': len({r.get('mask_pixel_sha256') for r in originals}) == 1 if complete and len(originals) >= 2 else None})
            first = originals[0]
            summary.append({'id': row['id'], 'source_kind': row['source_kind'], 'mode': mode,
                            'pipeline_success': first['pipeline_success'],
                            'geometric_proposals': len(first.get('analysis', {}).get('objects', [])),
                            'proposal_classes': dict(Counter(o['class'] for o in first.get('analysis', {}).get('objects', [])))})
    return {'schema_version': 1, 'evaluation_type': 'unlabelled_real_input_probe',
            'manifest_sha256': sha256(manifest),
            'runtime': {'python': platform.python_version(), 'pillow': PIL.__version__},
            'parameters': {'variants': list(variants), 'original_repeats': repeats, 'dim_factor': .55, 'rotation_degrees': 15}, 'distinct_sources': len(data['images']),
            'source_counts': dict(Counter(r['source_kind'] for r in data['images'])),
            'annotation_status': 'unlabelled', 'recognition_accuracy': None,
            'localization_accuracy': None, 'semantic_recognition_evaluated': False,
            'representative_generalization_validated': False,
            'attempted_runs': len(cases), 'successful_runs': sum(r['pipeline_success'] for r in cases),
            'summary': summary, 'repeatability': stability, 'results': cases,
            'limitations': ['Geometric proposals have no confirmed truth labels or boxes.',
                            'Screenshots are not independent camera captures.',
                            'Synthetic dimming/rotation does not create new photographs.',
                            'Repeated outputs establish repeatability, not correctness.',
                            'No hand, furniture, text/OCR or diagram semantics were recognized by this engine.']}
