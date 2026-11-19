#!/usr/bin/env python3
"""Create a hash-bound draft annotation template; no truth labels are invented."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from seye.core.storage import atomic_json
from seye.image.ingestion import load_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-kind', choices=('photograph', 'screenshot'), required=True)
    parser.add_argument('--annotator', required=True)
    args = parser.parse_args()
    root = args.directory.resolve()
    if args.output.resolve().parent != root:
        parser.error('Save manifest beside input images to preserve relative paths')
    rows = []
    for path in sorted(root.iterdir()):
        if path.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            image, source = load_image(path, allowed_root=root)
            rows.append({'id': path.name, 'path': path.name, 'sha256': source['sha256'],
                         'source_kind': args.source_kind, 'annotation_status': 'draft', 'annotator': args.annotator,
                         'capture_group': 'REVIEW_CAPTURE_GROUP', 'instances': [],
                         'review_note': 'EMPTY TEMPLATE: add reviewed instance boxes; empty does not assert a negative image.'})
    atomic_json(args.output, {'schema_version': 1, 'coordinate_space': 'exif_oriented_source',
                              'template_unscored': True, 'images': rows})
    print(args.output)
