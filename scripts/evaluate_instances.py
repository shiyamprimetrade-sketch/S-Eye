#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from seye.core.storage import atomic_json
from seye.detection.annotations import evaluate_annotations

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Versioned instance and dark-stroke mask evaluation')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--split', choices=('train', 'validation', 'test'))
    parser.add_argument('--mode', choices=('baseline', 'adaptive'), default='baseline')
    args = parser.parse_args()
    try:
        result = evaluate_annotations(args.manifest, args.mode, args.split)
        atomic_json(args.output, result)
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + '\n')
    print(args.output)
    raise SystemExit(int(any(not row['success'] for row in result['results'])))
