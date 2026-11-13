"""Versioned, bounded instance annotations and multi-image localization scoring."""
import hashlib
from pathlib import Path
from PIL import Image
from seye.core.storage import read_json
from seye.core.datasets import validate_splits
from seye.image.ingestion import load_image
from seye.detection.analysis import analyze
from seye.detection.metrics import valid_box, detection_metrics, mask_iou


def validate_annotations(manifest):
    manifest = Path(manifest).resolve()
    data = read_json(manifest)
    if not isinstance(data, dict) or data.get('schema_version') != 1 or data.get('coordinate_space') != 'exif_oriented_source':
        raise ValueError('Expected schema-1 annotations in EXIF-oriented source coordinates')
    if data.get('template_unscored') is True:
        raise ValueError('Annotation template must be reviewed before scoring')
    images = data.get('images')
    if not isinstance(images, list) or not 1 <= len(images) <= 1000:
        raise ValueError('Expected 1..1000 annotated images')
    seen, hashes = set(), set()
    for row in images:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'] or row['id'] in seen:
            raise ValueError('Unique nonempty image IDs required')
        seen.add(row['id'])
        if not isinstance(row.get('path'), str):
            raise ValueError('Image path required')
        image, source = load_image(manifest.parent / row['path'], allowed_root=manifest.parent)
        if row.get('sha256') != source['sha256'] or source['sha256'] in hashes:
            raise ValueError('Image hash mismatch or duplicate bytes')
        hashes.add(source['sha256'])
        if row.get('source_kind') not in ('synthetic', 'photograph', 'screenshot'):
            raise ValueError('Explicit source kind required')
        if row.get('annotation_status') not in ('generator', 'draft', 'human_reviewed'):
            raise ValueError('Explicit annotation status required')
        if (row['annotation_status'] == 'generator') != (row['source_kind'] == 'synthetic'):
            raise ValueError('Generator annotations require synthetic sources and vice versa')
        if not isinstance(row.get('annotator'), str) or not row['annotator'].strip():
            raise ValueError('Annotation provenance required')
        if not isinstance(row.get('capture_group'), str) or not row['capture_group']:
            raise ValueError('Capture group required')
        instances = row.get('instances')
        if not isinstance(instances, list) or len(instances) > 256:
            raise ValueError('At most 256 annotated instances per image')
        ids = set()
        for instance in instances:
            if not isinstance(instance, dict):
                raise ValueError('Instance must be an object')
            if not isinstance(instance.get('id'), str) or instance['id'] in ids or not instance['id']:
                raise ValueError('Unique instance IDs required')
            ids.add(instance['id'])
            if not isinstance(instance.get('class'), str) or not instance['class']:
                raise ValueError('Instance class required')
            valid_box(instance['box'])
            x1, y1, x2, y2 = instance['box']
            if not (0 <= x1 < x2 <= image.width and 0 <= y1 < y2 <= image.height):
                raise ValueError('Annotation box outside oriented source')
        if 'mask' in row:
            if row.get('mask_scope') != 'dark_strokes':
                raise ValueError('Current API can only score dark-stroke masks')
            mask, provenance = load_image(manifest.parent / row['mask'], allowed_root=manifest.parent)
            if provenance['sha256'] != row.get('mask_sha256') or mask.size != image.size:
                raise ValueError('Mask identity or oriented grid mismatch')
            if not set(mask.convert('L').get_flattened_data()).issubset({0, 255}):
                raise ValueError('Ground truth mask must be binary')
    if any('split' in row for row in images):
        validate_splits(images, manifest.parent)
    return data


def evaluate_annotations(manifest, mode='baseline', split=None, iou_threshold=.5):
    manifest = Path(manifest).resolve()
    data = validate_annotations(manifest)
    if split is not None and split not in ('train', 'validation', 'test'):
        raise ValueError('Invalid split')
    selected = [row for row in data['images'] if split is None or row.get('split') == split]
    if not selected:
        raise ValueError('Selected split is empty')
    results, partitions = [], {}
    for row in selected:
        record = {'id': row['id'], 'source_kind': row['source_kind'],
                  'annotation_status': row['annotation_status'], 'split': row.get('split', 'unsplit'),
                  'source_sha256': row['sha256']}
        try:
            report, artifacts = analyze(manifest.parent / row['path'], mode, manifest.parent)
            predictions = [{'class': obj['class'], 'box': obj['source_box']} for obj in report['objects']]
            metrics = detection_metrics(row['instances'], predictions, iou_threshold)
            record.update(success=True, expected=row['instances'], predicted=predictions, metrics=metrics)
            if 'mask' in row:
                mask, _ = load_image(manifest.parent / row['mask'], allowed_root=manifest.parent)
                truth = mask.convert('L').resize(artifacts['mask'].size, Image.Resampling.NEAREST)
                record['stroke_mask_iou'] = mask_iou(truth, artifacts['mask'])
        except (ValueError, OSError) as error:
            record.update(success=False, error=str(error), expected_instance_count=len(row['instances']))
        results.append(record)
        key = (record['source_kind'], record['annotation_status'], record['split'])
        group = partitions.setdefault(key, {'attempted_images': 0, 'pipeline_failures': 0, 'tp': 0, 'fp': 0, 'fn': 0})
        group['attempted_images'] += 1
        if record['success']:
            for metric in ('tp', 'fp', 'fn'):
                group[metric] += record['metrics'][metric]
        else:
            group['pipeline_failures'] += 1
    summaries = []
    for (kind, annotation, subset), counts in sorted(partitions.items()):
        tp, fp, fn = (counts[k] for k in ('tp', 'fp', 'fn'))
        summaries.append(dict(counts, source_kind=kind, annotation_status=annotation, split=subset,
                              precision=tp / (tp + fp) if tp + fp else None,
                              recall=tp / (tp + fn) if tp + fn else None))
    return {'schema_version': 1, 'evaluation_type': 'instance_box_and_stroke_mask',
            'mode': mode, 'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
            'representative_validation': False, 'summaries': summaries, 'results': results,
            'limitations': ['Failures are counted separately, not invented as classifier predictions.',
                            'Annotation review metadata is declared, not authenticated.',
                            'Generator/draft/human-reviewed partitions never mix.',
                            'Representative validation requires independently reviewed data and protocol.']}
