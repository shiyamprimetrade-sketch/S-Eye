from PIL import Image
from collections import deque

image = Image.open("paperless_shapes.png").convert("L")
width, height = image.size
pixels = image.load()

dark = {
    (x, y)
    for y in range(height)
    for x in range(width)
    if pixels[x, y] < 128
}

regions = []

while dark:
    start = dark.pop()
    queue = deque([start])
    region = [start]

    while queue:
        x, y = queue.popleft()

        for point in (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ):
            if point in dark:
                dark.remove(point)
                queue.append(point)
                region.append(point)

    if len(region) >= 100:
        regions.append(region)

regions.sort(key=lambda r: min(x for x, y in r))

print("S-Eye: Automatic recognition")
print("Objects detected:", len(regions))

predictions = []

for number, region in enumerate(regions, 1):
    xs = [x for x, y in region]
    ys = [y for x, y in region]

    w = max(xs) - min(xs) + 1
    h = max(ys) - min(ys) + 1

    fill = len(region) / (w * h)
    aspect = w / h

    if fill > 0.90:
        shape = "Square" if 0.85 <= aspect <= 1.15 else "Rectangle"
    elif fill > 0.65 and 0.85 <= aspect <= 1.15:
        shape = "Circle"
    elif 0.35 <= fill <= 0.65:
        shape = "Triangle-like"
    else:
        shape = "Unknown"

    predictions.append(shape)

    print(
        f"Object {number}: {shape} "
        f"(fill={fill:.3f}, aspect={aspect:.2f})"
    )

expected = ["Circle", "Square", "Triangle-like"]

passed = predictions == expected

print("Expected:", expected)
print("Detected:", predictions)
print("Test:", "PASS" if passed else "FAIL")
