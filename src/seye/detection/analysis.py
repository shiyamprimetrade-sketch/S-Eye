"""Opt-in structured geometric localization; not general object recognition."""
from math import hypot
from PIL import Image
from seye.geometry.hull import hull, simplify
from seye.image.ingestion import load_image
from seye.segmentation.regions import segment, components


def classify(points):
    outline = hull(points)
    xs, ys = zip(*points)
    corners = simplify(outline, max(max(xs) - min(xs) + 1, max(ys) - min(ys) + 1) * .08)
    count = len(corners)
    if count == 3:
        label = 'Triangle'
    elif count == 4:
        sides = [hypot(corners[(i + 1) % 4][0] - corners[i][0],
                       corners[(i + 1) % 4][1] - corners[i][1]) for i in range(4)]
        ratio = min(sides) / max(sides)
        label = 'Square-like' if ratio >= .95 else ('Ambiguous quadrilateral' if ratio >= .75 else 'Rectangle-like')
    elif count >= 5:
        label = 'Circle-like'
    else:
        label = 'Unknown'
    return {'label': label, 'corners': count, 'hull_vertices': len(outline),
            'class': {'Triangle': 'triangle', 'Circle-like': 'circle', 'Unknown': 'unknown'}.get(label, 'quadrilateral')}


def analyze(path, mode='baseline', allowed_root=None):
    source, provenance = load_image(path, allowed_root=allowed_root)
    processed = source.copy()
    processed.thumbnail((300, 400))  # Match Stage 84 preprocessing.
    mask = segment(processed, mode)
    grouped, regions = components(mask)
    objects, rejected = [], []
    scale_x, scale_y = source.width / processed.width, source.height / processed.height
    for points in regions:
        xs, ys = zip(*points)
        box = [min(xs), min(ys), max(xs) + 1, max(ys) + 1]
        width, height = box[2] - box[0], box[3] - box[1]
        ratio = min(width, height) / max(width, height)
        if ratio < .45:
            rejected.append({'processed_box': box, 'reason': 'aspect_ratio_below_0.45'})
            continue
        objects.append({'id': len(objects) + 1, **classify(points), 'processed_box': box,
                        'source_box': [box[0] * scale_x, box[1] * scale_y, box[2] * scale_x, box[3] * scale_y],
                        'component_pixels': len(points), 'uncertainty': 'uncalibrated_geometric_hypothesis'})
    report = {'schema_version': 1, 'engine': 'seye-independent-geometry',
              'source': provenance, 'processed_size': list(processed.size),
              'box_convention': '[left, top, right, bottom), exclusive right/bottom',
              'segmentation_mode': mode, 'experimental': True,
              'objects': objects, 'rejected_regions': rejected,
              'semantic_object_recognition': False, 'confidence_calibrated': False,
              'limitations': ['Hull labels are geometric hypotheses.',
                              'Overlapping objects may merge; no instance separation guarantee.',
                              'Masks mark dark strokes and grouped pixels, not filled object silhouettes.',
                              'Adaptive mode is experimental and has no photographic validation.']}
    return report, {'mask': mask, 'grouped_mask': grouped, 'source': source}
