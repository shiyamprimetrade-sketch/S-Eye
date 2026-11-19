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


def git_paths(*arguments):
    raw = subprocess.check_output(['git', 'ls-files', '-z', *arguments], cwd=ROOT)
    return [name for name in raw.decode('utf-8').split('\0') if name]


def audit(output):
    inventory = read_json(ROOT / 'benchmarks/stage84_inventory.json')
    changed, relocated = [], {}
    for row in inventory['files']:
        name = row['path']
        path = ROOT / name
        archive = ROOT / 'legacy/stage84' / name
        if not path.exists() and '/' not in name and archive.is_file():
            path = archive
            relocated[name] = path.relative_to(ROOT).as_posix()
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            changed.append(name)
    if set(changed) - {'.gitignore', 'README.md'}:
        raise ValueError('Historical algorithm/checkpoint changed: ' + str(changed))
    tracked = set(git_paths('--cached'))
    paths = tracked | set(git_paths('--others', '--exclude-standard'))
    files = []
    for name in sorted(paths):
        path = ROOT / name
        if name == 'benchmarks/current_source_audit.json' or path == output.resolve():
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError('Audit requires a regular repository file: ' + name)
        raw = path.read_bytes()
        if path.suffix == '.py':
            ast.parse(raw, filename=name)
        files.append({'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    return {'schema_version': 1, 'scope': 'working-tree snapshot relative to parent; output excludes itself',
            'parent_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'baseline_commit': inventory['baseline_commit'], 'changed_baseline_files': changed,
            'relocated_baseline_files': relocated,
            'python_syntax': 'all parsed successfully', 'files': files}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); atomic_json(args.output, audit(args.output)); print(args.output)
