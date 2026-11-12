#!/usr/bin/env python3
"""Working-tree file inventory, Python syntax and Stage 84 preservation audit."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from seye.core.storage import atomic_json, read_json


def audit(output):
    inventory = read_json(ROOT / 'benchmarks/stage84_inventory.json')
    changed = [r['path'] for r in inventory['files'] if hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() != r['sha256']]
    if set(changed) - {'.gitignore', 'README.md'}:
        raise ValueError('Historical algorithm/checkpoint changed: ' + str(changed))
    paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    files = []
    for name in sorted(set(paths)):
        path = ROOT / name
        if not path.is_file() or name == 'benchmarks/current_source_audit.json' or path.resolve() == output.resolve():
            continue
        if path.suffix == '.py':
            ast.parse(path.read_text())
        files.append({'path': name, 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return {'schema_version': 1, 'scope': 'working-tree snapshot relative to parent; output excludes itself',
            'parent_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'baseline_commit': inventory['baseline_commit'], 'changed_baseline_files': changed,
            'python_syntax': 'all parsed successfully', 'files': files}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); atomic_json(args.output, audit(args.output)); print(args.output)
