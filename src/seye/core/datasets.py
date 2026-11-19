"""Deterministic grouped splits and conservative near-duplicate leakage audits.

This heuristic identifies some recaptures/edits; it cannot certify scene independence.
Capture groups supplied by reviewers remain the primary leakage boundary.
"""
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageOps

SPLITS = ('train', 'validation', 'test')
POLICY = {'name': 'capture-and-content-v1', 'thumbnail_size': 32, 'resampling': 'bilinear',
          'dhash_bits': 64, 'max_hamming': 6, 'max_normalized_mae': 0.15,
          'max_aspect_ratio_difference': 0.02,
          'max_images': 2000,
          'limitation': 'Heuristic only: viewpoint, crop, occlusion and similar scenes require capture-group review.'}


def fingerprint(path):
    """EXIF-canonical pixel identity plus brightness/contrast-tolerant descriptors."""
    with Image.open(path) as original:
        rgb = ImageOps.exif_transpose(original).convert('RGB')
        identity = hashlib.sha256(
            f'{rgb.width}x{rgb.height}:RGB:'.encode() + rgb.tobytes()).hexdigest()
        gray = rgb.convert('L')
        small = list(gray.resize((32, 32), Image.Resampling.BILINEAR).get_flattened_data())
        mean = sum(small) / len(small)
        std = max(1.0, math.sqrt(sum((p - mean) ** 2 for p in small) / len(small)))
        normalized = tuple(round((p - mean) / std, 6) for p in small)
        pixels = list(gray.resize((9, 8), Image.Resampling.BILINEAR).get_flattened_data())
        dhash = 0
        for y in range(8):
            for x in range(8):
                dhash = (dhash << 1) | (pixels[y * 9 + x] > pixels[y * 9 + x + 1])
        return {'pixel_sha256': identity, 'dhash': dhash,
                'aspect_ratio': rgb.width / rgb.height, 'normalized': normalized}


def pair_reason(first, second):
    if first['pixel_sha256'] == second['pixel_sha256']:
        return 'decoded_duplicate'
    if abs(first['aspect_ratio'] / second['aspect_ratio'] - 1) > POLICY['max_aspect_ratio_difference']:
        return None
    if (first['dhash'] ^ second['dhash']).bit_count() > POLICY['max_hamming']:
        return None
    error = sum(abs(a - b) for a, b in zip(first['normalized'], second['normalized'])) / 1024
    return 'near_duplicate' if error <= POLICY['max_normalized_mae'] else None


def audit(rows, directory):
    """Return transitive capture/content components and all cross-split conflicts."""
    if not rows or len(rows) > POLICY['max_images']:
        raise ValueError(f"Dataset requires 1..{POLICY['max_images']} images for pairwise audit")
    directory = Path(directory).resolve()
    parents, descriptors, identifiers = {}, {}, set()
    by_id = {}
    for row in rows:
        identifier = row.get('id')
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError('Image IDs must be nonempty and unique')
        identifiers.add(identifier)
        by_id[identifier] = row
        if not isinstance(row.get('capture_group'), str) or not row['capture_group'].strip():
            raise ValueError('capture_group is required for leakage auditing')
        if not isinstance(row.get('path'), str):
            raise ValueError('Image path required')
        path = (directory / row['path']).resolve()
        if not path.is_relative_to(directory):
            raise ValueError('Image escapes dataset directory')
        if hashlib.sha256(path.read_bytes()).hexdigest() != row.get('sha256'):
            raise ValueError(f'Source hash mismatch: {identifier}')
        descriptors[identifier] = fingerprint(path)
        parents[identifier] = identifier

    def find(value):
        while parents[value] != value:
            parents[value] = parents[parents[value]]
            value = parents[value]
        return value

    def union(a, b):
        a, b = find(a), find(b)
        parents[max(a, b)] = min(a, b)

    links = []
    ids = sorted(identifiers)
    for number, first in enumerate(ids):
        for second in ids[number + 1:]:
            a, b = by_id[first], by_id[second]
            if a['sha256'] == b['sha256']:
                reason = 'byte_duplicate'
            elif a['capture_group'] == b['capture_group']:
                reason = 'capture_group'
            else:
                reason = pair_reason(descriptors[first], descriptors[second])
            if reason:
                union(first, second)
                links.append({'first': first, 'second': second, 'reason': reason})
    grouped = {}
    for identifier in ids:
        grouped.setdefault(find(identifier), []).append(identifier)
    components = sorted(grouped.values())
    assigned = [r.get('split') for r in rows]
    has_splits = any(value is not None for value in assigned)
    conflicts = []
    if has_splits:
        if any(value not in SPLITS for value in assigned):
            raise ValueError('Every image must have a valid train/validation/test split')
        for component in components:
            splits = sorted({by_id[identifier]['split'] for identifier in component})
            if len(splits) > 1:
                conflicts.append({'ids': component, 'splits': splits})
    return {'schema_version': 1, 'policy': POLICY.copy(), 'source_count': len(rows),
            'component_count': len(components), 'components': components,
            'links': links, 'splits_present': has_splits, 'conflicts': conflicts,
            'leakage_detected': bool(conflicts),
            'fingerprints': {i: {'pixel_sha256': descriptors[i]['pixel_sha256'],
                                 'dhash_hex': f"{descriptors[i]['dhash']:016x}"} for i in ids}}


def validate_splits(rows, directory):
    report = audit(rows, directory)
    if report['leakage_detected']:
        raise ValueError('Dataset leakage across splits: ' + json.dumps(report['conflicts']))
    return report


def assign_splits(data, directory, seed=85, ratios=(0.6, 0.2, 0.2)):
    """Allocate indivisible components, never individual images; no model training."""
    if type(seed) is not int:
        raise ValueError('seed must be an integer')
    if len(ratios) != 3 or any(not math.isfinite(x) or x <= 0 for x in ratios) or abs(sum(ratios) - 1) > 1e-9:
        raise ValueError('Three positive finite ratios must sum to one')
    # Preserve an existing allocation: resplitting requires a new source manifest.
    if any('split' in row for row in data['images']):
        raise ValueError('Refusing to overwrite existing splits')
    report = audit(data['images'], directory)
    components = report['components']
    if len(components) < 3:
        raise ValueError('Need at least three independent capture/content components')
    total = len(components)
    counts = [max(1, int(total * ratio)) for ratio in ratios]
    while sum(counts) > total:
        index = max((i for i in range(3) if counts[i] > 1), key=lambda i: counts[i] - total * ratios[i])
        counts[index] -= 1
    while sum(counts) < total:
        index = max(range(3), key=lambda i: total * ratios[i] - counts[i])
        counts[index] += 1
    ordered = sorted(components, key=lambda c: hashlib.sha256(
        json.dumps([seed, c], separators=(',', ':')).encode()).hexdigest())
    assignment, cursor = {}, 0
    for split, count in zip(SPLITS, counts):
        for component in ordered[cursor:cursor + count]:
            for identifier in component:
                assignment[identifier] = split
        cursor += count
    result = json.loads(json.dumps(data))
    for row in result['images']:
        row['split'] = assignment[row['id']]
    result['split_provenance'] = {'seed': seed, 'ratios': list(ratios),
                                'allocation_unit': 'capture/content connected component',
                                'component_counts': dict(zip(SPLITS, counts)),
                                'policy': POLICY.copy()}
    validate_splits(result['images'], directory)
    return result
