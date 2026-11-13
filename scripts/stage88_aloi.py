#!/usr/bin/env python3
"""Acquire a bounded ALOI research subset; never promote object names to shape truth."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from PIL import Image, ImageDraw
from seye.core.capture_protocol import assess
from seye.core.probes import validate_manifest
from seye.core.storage import atomic_json

OBJECTS = {4: 'Round candle', 16: 'Red block', 19: 'Green block'}
CONDITIONS = ('l1c1', 'l3c1', 'l8c1', 'r0', 'r30', 'r60')
BASE = 'https://aloi.science.uva.nl/'
MAX_ARCHIVE = 16 * 1024 * 1024
SOURCES = {'description': BASE + 'aloi/description.html',
           'downloads': BASE + 'aloi/download.html',
           'object_annotations': BASE + 'aloi/annotation.pdf'}


def selected_images(blob, object_id):
    """Read selected regular files only; never extract archive-controlled paths."""
    if object_id not in OBJECTS or len(blob) > MAX_ARCHIVE:
        raise ValueError('Unsupported object or oversized archive')
    wanted = {f'png4/{object_id}/{object_id}_{c}.png': c for c in CONDITIONS}
    result = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:') as archive:
        for member in archive:
            if member.name not in wanted:
                continue
            condition = wanted[member.name]
            if condition in result or not member.isfile() or not 0 < member.size <= 1024 * 1024:
                raise ValueError('Invalid selected archive member')
            payload = archive.extractfile(member).read()
            with Image.open(io.BytesIO(payload)) as image:
                if image.format != 'PNG' or image.size != (192, 144):
                    raise ValueError('Expected quarter-resolution ALOI PNG')
                image.load()
            result[condition] = payload
    if set(result) != set(CONDITIONS):
        raise ValueError('Incomplete selected captures')
    return result


def capture_row(object_id, condition, payload):
    rotation = condition.startswith('r')
    return {'id': f'aloi-{object_id}-{condition}',
            'path': f'images/{object_id}_{condition}.png',
            'sha256': hashlib.sha256(payload).hexdigest(), 'source_kind': 'photograph',
            'target_group': f'aloi-object-{object_id}',
            'source_object_name': OBJECTS[object_id],
            'source_archive': BASE + f'tars/png4/{object_id}.tar',
            'source_member': f'png4/{object_id}/{object_id}_{condition}.png',
            'capture_condition': condition,
            # r-series uses fixed frontal camera and a physically rotated object.
            'camera_angle': f'frontal camera; object yaw {condition[1:]} degrees' if rotation else 'frontal camera; object yaw 0 degrees',
            'lighting': 'all five lamps (view series)' if rotation else condition[:-2],
            'annotation_status': 'unlabelled_for_geometric_recognition'}


def acquire(destination, expected=None):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Use a new output directory to preserve prior acquisitions')
    # Download and validate everything before writing the output directory.
    def fetch(object_id):
        url = BASE + f'tars/png4/{object_id}.tar'
        with urllib.request.urlopen(url, timeout=60) as response:
            blob = response.read(MAX_ARCHIVE + 1)
        return object_id, selected_images(blob, object_id), hashlib.sha256(blob).hexdigest()
    with ThreadPoolExecutor(max_workers=3) as pool:
        downloads = list(pool.map(fetch, OBJECTS))
    rows = [capture_row(oid, c, captures[c]) for oid, captures, _ in downloads for c in CONDITIONS]
    if expected is not None:
        actual = {r['id']: r['sha256'] for r in rows}
        if actual != {r['id']: r['sha256'] for r in expected['images']}:
            raise ValueError('Source differs from pinned acquisition; no output written')
    destination.mkdir(parents=True)
    (destination / 'images').mkdir()
    for oid, captures, _ in downloads:
        for c, payload in captures.items():
            (destination / 'images' / f'{oid}_{c}.png').write_bytes(payload)
    manifest = {'schema_version': 1, 'annotation_status': 'unlabelled',
                'dataset': 'ALOI', 'sources': SOURCES,
                'physical_capture_conditions': 'ALOI documented same-object lighting l1/l3/l8 and physical object orientations 0/30/60 degrees; fixed frontal camera; not a factorial lighting-by-angle experiment',
                'archive_sha256': {str(oid): digest for oid, _, digest in downloads},
                'usage': 'Scientific research; copyright ISIS, University of Amsterdam. No permissive redistribution license asserted.',
                'images': rows}
    atomic_json(destination / 'manifest.json', manifest)
    validate_manifest(destination / 'manifest.json')
    atomic_json(destination / 'capture_gate.json', assess(rows))
    sheet = Image.new('RGB', (6 * 192, 3 * 168), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(rows):
        x, y = (i % 6) * 192, (i // 6) * 168
        with Image.open(destination / row['path']) as image:
            sheet.paste(image, (x, y))
        draw.text((x + 3, y + 146), row['id'], fill='black')
    sheet.save(destination / 'contact_sheet.jpg')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected', type=Path, help='Previously reviewed acquisition manifest; require identical source hashes')
    args = parser.parse_args()
    result = acquire(args.output, json.loads(args.expected.read_text()) if args.expected else None)
    print(json.dumps({'images': len(result['images']), 'output': str(args.output), 'recognition_accuracy': None}))
