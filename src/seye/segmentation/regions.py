"""Independent local-contrast masks and deterministic connected components."""
from collections import deque
from math import sqrt
from PIL import Image, ImageFilter


def segment(image, mode='baseline'):
    gray = image.convert('L')
    if mode == 'baseline':
        background = gray.filter(ImageFilter.GaussianBlur(radius=15))
        mask = Image.new('L', gray.size)
        mask.putdata([255 if b - p > 18 else 0
                      for p, b in zip(gray.get_flattened_data(), background.get_flattened_data())])
        return mask
    if mode != 'adaptive':
        raise ValueError('Segmentation mode must be baseline or adaptive')
    # Experimental independent local mean/variance rule using summed-area tables.
    # Dark-pixel evidence must exceed max(3, 0.2*local_std). No learned weights.
    width, height = gray.size
    stride = width + 1
    sums, squares = [0] * ((height + 1) * stride), [0] * ((height + 1) * stride)
    pixels = list(gray.get_flattened_data())
    for y in range(height):
        total = total_square = 0
        for x in range(width):
            value = pixels[y * width + x]
            total += value
            total_square += value * value
            index = (y + 1) * stride + x + 1
            sums[index] = sums[index - stride] + total
            squares[index] = squares[index - stride] + total_square

    def rectangle(table, left, top, right, bottom):
        return table[bottom * stride + right] - table[top * stride + right] - table[bottom * stride + left] + table[top * stride + left]

    output = []
    for y in range(height):
        for x in range(width):
            left, right = max(0, x - 15), min(width, x + 16)
            top, bottom = max(0, y - 15), min(height, y + 16)
            area = (right - left) * (bottom - top)
            mean = rectangle(sums, left, top, right, bottom) / area
            variance = max(0, rectangle(squares, left, top, right, bottom) / area - mean * mean)
            threshold = max(3, .2 * sqrt(variance))
            output.append(255 if mean - pixels[y * width + x] > threshold else 0)
    mask = Image.new('L', gray.size)
    mask.putdata(output)
    return mask


def components(mask, minimum_area=100):
    grouped = mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    width, height = grouped.size
    remaining = {i for i, value in enumerate(grouped.get_flattened_data()) if value > 128}
    regions = []
    # Row-major starts and a geometric tie-break keep equal-area region IDs stable.
    for start in range(width * height):
        if start not in remaining:
            continue
        remaining.remove(start)
        queue = deque([start])
        points = []
        while queue:
            index = queue.popleft()
            x, y = index % width, index // width
            points.append((x, y))
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                neighbor = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        if len(points) >= minimum_area:
            regions.append(points)
    regions.sort(key=lambda points: (-len(points), min(y for x, y in points), min(x for x, y in points)))
    return grouped, regions
