#!/usr/bin/env python3
"""Stage 86: audit capture leakage or prepare reproducible grouped dataset splits."""
import argparse
import json
import sys
from pathlib import Path

# Incremental src layout; historical root commands continue to work without install.
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from seye.core.datasets import assign_splits, audit, validate_splits
from seye.core.evaluation import diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('audit', 'split'))
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=85)
    args = parser.parse_args()
    try:
        # Split manifests retain relative paths: keep them beside the source manifest.
        if args.output.exists():
            raise ValueError('Output exists; choose a new path')
        if args.command == 'split' and args.output.resolve().parent != args.manifest.resolve().parent:
            raise ValueError('Split manifest must be saved beside the source manifest')
        from generalization import load_manifest
        data = load_manifest(args.manifest, check_splits=False)
        if args.command == 'split':
            result = assign_splits(data, args.manifest.resolve().parent, args.seed)
        else:
            result = audit(data['images'], args.manifest.resolve().parent)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    except (ValueError, OSError) as error:
        parser.exit(2, f'Dataset error: {error}\n')
    print(args.output)
    return int(result.get('leakage_detected', False))


if __name__ == '__main__':
    raise SystemExit(main())
