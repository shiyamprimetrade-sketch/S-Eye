#!/usr/bin/env python3
"""Generated-instance localization and adaptive segmentation comparison."""
import argparse
import hashlib
import json
import platform
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
import PIL
from PIL import Image, ImageDraw, ImageEnhance, ImageOps
from seye.detection.analysis import analyze
from seye.detection.metrics import detection_metrics, mask_iou


def benchmark():
    scene = Image.new('RGB', (300, 300), 'white')
    draw = ImageDraw.Draw(scene)
    draw.ellipse((30, 40, 100, 110), outline='black', width=5)
    draw.rectangle((170, 40, 240, 110), outline='black', width=5)
    draw.polygon([(150, 180), (105, 270), (195, 270)], outline='black', width=5)
    boxes = [{'class': 'circle', 'box': [30, 40, 101, 111]},
             {'class': 'quadrilateral', 'box': [170, 40, 241, 111]},
             {'class': 'triangle', 'box': [105, 180, 196, 271]}]
    strokes = ImageOps.invert(scene.convert('L'))
    rotated_boxes = [{'class': row['class'],
                      'box': [row['box'][1], 300 - row['box'][2], row['box'][3], 300 - row['box'][0]]} for row in boxes]
    small_boxes = [{'class': row['class'], 'box': [v / 2 for v in row['box']]} for row in boxes]
    clutter = scene.copy()
    clutter_draw = ImageDraw.Draw(clutter)
    for x in range(10, 300, 20):
        clutter_draw.line((x, 0, x, 299), fill=(70, 70, 70), width=1)
    cases = [('original', scene, boxes, strokes),
             ('dim', ImageEnhance.Brightness(scene).enhance(.55), boxes, strokes),
             ('faint', ImageEnhance.Contrast(scene).enhance(.06), boxes, strokes),
             ('rotate90', scene.transpose(Image.Transpose.ROTATE_90), rotated_boxes,
              strokes.transpose(Image.Transpose.ROTATE_90)),
             ('half_scale', scene.resize((150, 150), Image.Resampling.BILINEAR), small_boxes,
              strokes.resize((150, 150), Image.Resampling.NEAREST)),
             ('clutter', clutter, boxes, None),
             ('blank', Image.new('RGB', (300, 300), 'white'), [], Image.new('L', (300, 300)))]
    results = []
    with tempfile.TemporaryDirectory(prefix='s_eye_localization_') as directory:
        for name, image, expected, mask in cases:
            path = Path(directory) / f'{name}.png'
            image.save(path)
            for mode in ('baseline', 'adaptive'):
                start = time.perf_counter()
                report, artifacts = analyze(path, mode)
                seconds = time.perf_counter() - start
                predicted = [{'class': row['class'], 'box': row['source_box']} for row in report['objects']]
                results.append({'case': name, 'mode': mode, 'source_sha256': report['source']['sha256'],
                                'expected': expected, 'predicted': predicted,
                                'detection_metrics': detection_metrics(expected, predicted, threshold=.5),
                                'stroke_mask_iou': mask_iou(mask, artifacts['mask']) if mask is not None else None,
                                'mask_metric_scope': 'generator dark strokes, not filled silhouettes' if mask is not None else 'not evaluated with clutter',
                                'wall_seconds': seconds})
    summaries = []
    for mode in ('baseline', 'adaptive'):
        rows = [row for row in results if row['mode'] == mode]
        tp, fp, fn = (sum(row['detection_metrics'][metric] for row in rows) for metric in ('tp', 'fp', 'fn'))
        summaries.append({'mode': mode, 'cases': len(rows), 'tp': tp, 'fp': fp, 'fn': fn,
                          'precision': tp / (tp + fp) if tp + fp else None,
                          'recall': tp / (tp + fn) if tp + fn else None})
    files = sorted((ROOT / 'src/seye').rglob('*.py')) + [Path(__file__).resolve()]
    return {'schema_version': 1, 'milestone': 'Stage 90 experimental localization API',
            'source_kind': 'synthetic', 'representative_photo_validation': False,
            'independent_photographs': 0, 'base_generated_scenes': 1, 'generated_blank_controls': 1,
            'runtime': {'python': platform.python_version(), 'pillow': PIL.__version__,
                        'system': platform.system(), 'machine': platform.machine()},
            'code_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
            'limitations': ['Variants share one generated base scene; no independent sample accuracy.',
                            'Baseline/adaptive comparisons are exploratory, not held-out model validation.',
                            'Background grid is an unsupported clutter stress case.',
                            'Timing is a single host observation; no Android/Windows or streaming claim.'],
            'summary': summaries, 'results': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists')
    result = benchmark()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result['summary'], indent=2))
