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
    parser.add_argument('--config', type=Path)
    parser.add_argument('--read-root', action='append', default=[])
    parser.add_argument('--write-root', action='append', default=[])
    parser.add_argument('--allow-memory', action='store_true')
    parser.add_argument('--allow-training', action='store_true')
    parser.add_argument('--allow-video', action='store_true')
    parser.add_argument('--timeout', type=float)
    args = parser.parse_args()
    if args.config:
        from seye.core.configuration import load_config
        try:
            config = load_config(args.config)
        except (ValueError, OSError) as error:
            parser.exit(2, f'Configuration rejected: {error}\n')
        base = config['permissions']
    else:
        config = {'timeout': 30}; base = Permissions()
    grants = Permissions(tuple(args.read_root) if args.read_root else base.read_roots,
                         tuple(args.write_root) if args.write_root else base.write_roots,
                         args.allow_memory or base.memory, args.allow_training or base.training, args.allow_video or base.video)
    deadline = args.timeout if args.timeout is not None else config['timeout']
    try:
        output = grants.require(args.output, write=True)
        request = read_json(grants.require(args.request))
        response = bounded_handle(request, grants, deadline)
        atomic_json(output, response)
    except (ValueError, OSError) as error:
        parser.exit(2, f'Workflow failed: {error}\n')
    print(json.dumps({'success': response['success'], 'output': str(output)}))
    return 0 if response['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
