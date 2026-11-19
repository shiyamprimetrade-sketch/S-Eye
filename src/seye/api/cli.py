"""Local structured image-analysis CLI; no camera or memory access at import."""
import argparse
import json
from pathlib import Path
from PIL import ImageDraw
from seye.detection.analysis import analyze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--allowed-root', type=Path)
    parser.add_argument('--mode', choices=('baseline', 'adaptive'), default='baseline')
    args = parser.parse_args()
    try:
        if args.output_dir.exists():
            raise ValueError('Output directory exists; choose a new directory')
        report, images = analyze(args.image, args.mode, args.allowed_root)
        # Analysis completes before any output is created. Exclusive mkdir avoids overwrites.
        args.output_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
        images['mask'].save(args.output_dir / 'mask.png')
        images['grouped_mask'].save(args.output_dir / 'grouped_mask.png')
        overlay = images['source'].copy()
        draw = ImageDraw.Draw(overlay)
        for obj in report['objects']:
            box = obj['source_box']
            draw.rectangle(box, outline='red', width=2)
            draw.text((box[0], max(0, box[1] - 12)), f"{obj['id']}: {obj['label']}", fill='red')
        overlay.save(args.output_dir / 'overlay.png')
        with (args.output_dir / 'analysis.json').open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    except (OSError, ValueError) as error:
        parser.exit(2, f'Analysis failed: {error}\n')
    print(args.output_dir / 'analysis.json')
    return 0
