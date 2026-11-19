"""CLI for permission-scoped local JSON workflows and dataset/model experiments."""
import argparse
import json
from pathlib import Path
from seye.core.storage import read_json, atomic_json
from seye.integration.service import Permissions, bounded_handle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--describe-contract', action='store_true')
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--config', type=Path)
    parser.add_argument('--read-root', action='append', default=[])
    parser.add_argument('--write-root', action='append', default=[])
    parser.add_argument('--allow-memory', action='store_true')
    parser.add_argument('--allow-training', action='store_true')
    parser.add_argument('--allow-video', action='store_true')
    parser.add_argument('--timeout', type=float)
    args = parser.parse_args()
    if args.describe_contract:
        if args.request is not None or args.output is not None:parser.error('Contract description cannot be combined with request/output')
        from seye.integration.contracts import describe
        print(json.dumps(describe(),sort_keys=True))
        return 0
    if args.request is None or args.output is None:parser.error('--request and --output are required for execution')
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
        from seye.integration.contracts import decode_request
        with grants.require(args.request).open('rb') as stream:raw=stream.read(1024*1024+1)
        request=decode_request(raw,args.strict)
        response = bounded_handle(request, grants, deadline)
        atomic_json(output, response)
    except (ValueError, OSError) as error:
        parser.exit(2, f'Workflow failed: {error}\n')
    print(json.dumps({'success': response['success'], 'output': str(output)}))
    return 0 if response['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
