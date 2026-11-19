#!/usr/bin/env python3
"""Run unlabelled local photographs/screenshots without inventing accuracy."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from seye.core.probes import probe

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--overlays', type=Path)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('Output already exists')
        report = probe(args.manifest, overlay_directory=args.overlays)
        report['code_sha256'] = {str(p.relative_to(ROOT)): __import__('hashlib').sha256(p.read_bytes()).hexdigest()
                                 for p in sorted((ROOT / 'src/seye').rglob('*.py')) + [Path(__file__).resolve()]}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    except (ValueError, OSError) as error:
        parser.exit(2, f'Probe failed: {error}\n')
    print(json.dumps({k: report[k] for k in ('source_counts', 'attempted_runs', 'successful_runs', 'summary', 'repeatability')}, indent=2))
    raise SystemExit(0 if report['successful_runs'] == report['attempted_runs'] else 1)
