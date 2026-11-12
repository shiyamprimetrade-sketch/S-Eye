#!/usr/bin/env python3
"""Reproduce grouped synthetic evaluation; no photographic validation claim."""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dataset_tools import assign_splits, audit
from generalization import evaluate
from stage85_fixture import generate


def benchmark():
    with tempfile.TemporaryDirectory(prefix='s_eye_stage86_') as directory:
        manifest = generate(Path(directory) / 'synthetic', stress=True)
        data = assign_splits(json.loads(manifest.read_text()), manifest.parent, seed=85)
        split_manifest = manifest.parent / 'split.json'
        split_manifest.write_text(json.dumps(data, indent=2) + '\n')
        return {'milestone': 'Stage 86 grouped evaluation',
                'fixture_generator_sha256': hashlib.sha256((ROOT / 'stage85_fixture.py').read_bytes()).hexdigest(),
                'split_manifest': data, 'leakage_audit': audit(data['images'], manifest.parent),
                'evaluation': evaluate(split_manifest)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists')
    result = benchmark()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    rows = result['evaluation']['results']
    print(json.dumps({'sources': result['evaluation']['distinct_sources'], 'cases': len(rows),
                      'exact_matches': sum(r['metrics']['exact_match'] for r in rows),
                      'leakage_detected': result['leakage_audit']['leakage_detected']}))
