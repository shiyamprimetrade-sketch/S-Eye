"""Independent geometric, color, texture and spatial descriptors; no learned weights."""
import math
from PIL import Image, ImageOps

FEATURE_VERSION = 'seye-descriptors-v1'


def extract(image):
    image = ImageOps.exif_transpose(image).convert('RGB')
    image.thumbnail((256, 256))  # Bound descriptor workspace independently of source dimensions.
    gray = image.convert('L')
    values = list(gray.get_flattened_data())
    mean = sum(values) / len(values)
    std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
    threshold = mean - .5 * std
    mask = gray.point(lambda value: 255 if value < threshold else 0)
    box = mask.getbbox()
    if box:
        image = image.crop(box)
        mask = mask.crop(box)
    aspect = image.width / image.height
    occupancy = [v / 255 for v in mask.resize((8, 8), Image.Resampling.BOX).get_flattened_data()]
    rgb = list(image.resize((24, 24), Image.Resampling.BILINEAR).get_flattened_data())
    means = [sum(p[c] for p in rgb) / len(rgb) / 255 for c in range(3)]
    deviations = [math.sqrt(sum((p[c] / 255 - means[c]) ** 2 for p in rgb) / len(rgb)) for c in range(3)]
    histogram = [sum(min(p[c] // 64, 3) == b for p in rgb) / len(rgb) for c in range(3) for b in range(4)]
    ink = [(x, y, occupancy[y * 8 + x]) for y in range(8) for x in range(8)]
    mass = sum(p[2] for p in ink)
    cx = sum(x * w for x, y, w in ink) / mass if mass else 3.5
    cy = sum(y * w for x, y, w in ink) / mass if mass else 3.5
    moments = [mass / 64, cx / 7, cy / 7,
               sum((x - cx) ** 2 * w for x, y, w in ink) / max(mass, 1) / 49,
               sum((y - cy) ** 2 * w for x, y, w in ink) / max(mass, 1) / 49,
               sum((x - cx) * (y - cy) * w for x, y, w in ink) / max(mass, 1) / 49,
               aspect / (1 + aspect)]
    small = list(image.convert('L').resize((24, 24)).get_flattened_data())
    texture = [sum(abs(small[y * 24 + x] - small[y * 24 + x + 1]) for y in range(24) for x in range(23)) / (24 * 23 * 255),
               sum(abs(small[y * 24 + x] - small[(y + 1) * 24 + x]) for y in range(23) for x in range(24)) / (24 * 23 * 255)]
    return [round(float(v), 8) for v in occupancy + moments + means + deviations + histogram + texture]


def distance(first, second):
    if not first or len(first) != len(second) or any(type(v) not in (int, float) or not math.isfinite(v) for v in first + second):
        raise ValueError('Features must be same-length finite numeric vectors')
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(first, second)) / len(first))
