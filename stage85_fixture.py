#!/usr/bin/env python3
"""Generate reproducible synthetic camera-pipeline probes, never photographs."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from generalization import digest


def generate(destination, stress=False):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    rows = []
    shapes = ['circle', 'quadrilateral', 'triangle', 'blank']
    if stress:
        shapes += ['faint_triangle', 'tiny_circle', 'wide_quadrilateral']
    for shape in shapes:
        image = Image.new('RGB', (300, 300), 'white')
        draw = ImageDraw.Draw(image)
        if shape == 'circle':
            draw.ellipse((80, 80, 220, 220), outline='black', width=5)
        elif shape == 'quadrilateral':
            draw.rectangle((80, 80, 220, 220), outline='black', width=5)
        elif shape == 'triangle':
            draw.polygon([(150, 60), (70, 225), (230, 225)], outline='black', width=5)
        elif shape == 'faint_triangle':
            draw.polygon([(150, 60), (70, 225), (230, 225)], outline=(240, 240, 240), width=5)
        elif shape == 'tiny_circle':
            draw.ellipse((145, 145, 155, 155), outline='black', width=1)
        elif shape == 'wide_quadrilateral':
            draw.rectangle((30, 125, 270, 175), outline='black', width=5)
        photo = destination / f'{shape}.png'
        image.save(photo)
        rows.append({'id': shape, 'path': photo.name, 'sha256': digest(photo),
                     'source_kind': 'synthetic', 'human_confirmed': False,
                     'expected_classes': [] if shape == 'blank' else [shape.split('_')[-1]],
                     'capture_group': f'generated-{shape}', 'lighting': 'uniform_white',
                     'camera_angle': 'generated_frontal', 'annotation_source': 'stage85_fixture.py generator'})
    manifest = destination / 'manifest.json'
    manifest.write_text(json.dumps({'schema_version': 1, 'images': rows}, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--stress', action='store_true')
    args = parser.parse_args()
    print(generate(args.directory, args.stress))
