"""Opt-in edge, convex-boundary, denoising and projection-split experiments."""
from PIL import Image, ImageFilter
from seye.geometry.hull import hull


def edges(image, threshold=40):
    if type(threshold) is not int or not 0 <= threshold <= 255:
        raise ValueError('Edge threshold must be an integer in [0,255]')
    gray = image.convert('L'); width, height = gray.size
    pixels = gray.load(); result = Image.new('L', gray.size); output = result.load()
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            gx = -pixels[x-1, y-1] + pixels[x+1, y-1] - 2*pixels[x-1, y] + 2*pixels[x+1, y] - pixels[x-1, y+1] + pixels[x+1, y+1]
            gy = -pixels[x-1, y-1] - 2*pixels[x, y-1] - pixels[x+1, y-1] + pixels[x-1, y+1] + 2*pixels[x, y+1] + pixels[x+1, y+1]
            output[x, y] = 255 if abs(gx) + abs(gy) > threshold else 0
    return result


def denoise(mask):
    return mask.convert('L').filter(ImageFilter.MedianFilter(3))


def reconstruct(mask):
    return mask.convert('L').filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))


def convex_boundary(mask):
    points = [(x, y) for y in range(mask.height) for x in range(mask.width) if mask.getpixel((x, y)) > 128]
    return hull(points) if points else []


def projection_split(mask, minimum_area=100):
    """Split only at a deep interior x-projection valley; not general overlap separation."""
    mask = mask.convert('L'); pixels = mask.load()
    counts = [sum(pixels[x, y] > 128 for y in range(mask.height)) for x in range(mask.width)]
    occupied = [x for x, count in enumerate(counts) if count]
    if not occupied:
        return [mask.copy()]
    left, right = min(occupied), max(occupied)
    candidates = [x for x in range(left + (right-left)//5, right - (right-left)//5 + 1)
                  if 0 < counts[x] < max(counts) * .2]
    if not candidates:
        return [mask.copy()]
    cut = min(candidates, key=lambda x: (counts[x], abs(x - (left + right) / 2)))
    first, second = Image.new('L', mask.size), Image.new('L', mask.size)
    first.paste(mask.crop((0, 0, cut, mask.height)), (0, 0))
    second.paste(mask.crop((cut, 0, mask.width, mask.height)), (cut, 0))
    if min(sum(v > 128 for v in image.get_flattened_data()) for image in (first, second)) < minimum_area:
        return [mask.copy()]
    return [first, second]
