"""CLI for permission-scoped local JSON workflows and dataset/model experiments."""
import argparse
import json
from pathlib import Path
from seye.core.storage import read_json, atomic_json
from seye.integration.service import Permissions, bounded_handle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--read-root', action='append', default=[])
    parser.add_argument('--write-root', action='append', default=[])
    parser.add_argument('--allow-memory', action='store_true')
    parser.add_argument('--allow-training', action='store_true')
    parser.add_argument('--allow-video', action='store_true')
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args()
    grants = Permissions(tuple(args.read_root), tuple(args.write_root), args.allow_memory, args.allow_training, args.allow_video)
    try:
        output = grants.require(args.output, write=True)
        request = read_json(grants.require(args.request))
        response = bounded_handle(request, grants, args.timeout)
        atomic_json(output, response)
    except (ValueError, OSError) as error:
        parser.exit(2, f'Workflow failed: {error}\n')
    print(json.dumps({'success': response['success'], 'output': str(output)}))
    return 0 if response['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
