from PIL import Image, ImageDraw
from collections import deque

def create_shape(name):
    image = Image.new("L", (100, 100), 0)
    draw = ImageDraw.Draw(image)

    if name == "Circle":
        draw.ellipse((25, 25, 75, 75), fill=255)
    elif name == "Square":
        draw.rectangle((25, 25, 75, 75), fill=255)
    elif name == "Triangle":
        draw.polygon([(50, 20), (20, 80), (80, 80)], fill=255)

    return image

def analyze(image):
    pixels = image.load()
    points = [
        (x, y)
        for y in range(100)
        for x in range(100)
        if pixels[x, y] > 128
    ]

    left = min(x for x, y in points)
    right = max(x for x, y in points)
    top = min(y for x, y in points)
    bottom = max(y for x, y in points)

    width = right - left + 1
    height = bottom - top + 1
    area = len(points)
    fill_ratio = area / (width * height)

    if fill_ratio > 0.90:
        shape = "Square/Rectangle"
    elif fill_ratio > 0.65:
        shape = "Circle-like"
    else:
        shape = "Triangle-like"

    return shape, round(fill_ratio, 3)

correct = 0

for name in ("Circle", "Square", "Triangle"):
    image = create_shape(name)
    detected, ratio = analyze(image)

    expected = {
        "Circle": "Circle-like",
        "Square": "Square/Rectangle",
        "Triangle": "Triangle-like"
    }[name]

    passed = detected == expected
    correct += passed

    print(name, "->", detected)
    print("Fill ratio:", ratio)
    print("Test:", "PASS" if passed else "FAIL")

print("Tests passed:", correct, "/ 3")
