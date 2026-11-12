from PIL import Image
from collections import deque
from math import hypot

image = Image.open("geometry_challenge.png").convert("L")
pixels = image.load()

remaining = {
    (x, y)
    for y in range(image.height)
    for x in range(image.width)
    if pixels[x, y] < 128
}

def cross(o, a, b):
    return (
        (a[0]-o[0])*(b[1]-o[1])
        - (a[1]-o[1])*(b[0]-o[0])
    )

def hull(points):
    points = sorted(set(points))
    if len(points) <= 2:
        return points

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(
            lower[-2], lower[-1], p
        ) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(
            upper[-2], upper[-1], p
        ) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

def distance(p, a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = hypot(dx, dy)

    if length == 0:
        return hypot(p[0]-a[0], p[1]-a[1])

    return abs(
        dx*(a[1]-p[1])
        - (a[0]-p[0])*dy
    ) / length

def simplify(poly, tolerance):
    if len(poly) <= 3:
        return poly

    result = poly[:]

    while len(result) > 3:
        candidates = []

        for i in range(len(result)):
            a = result[i-1]
            p = result[i]
            b = result[(i+1) % len(result)]
            candidates.append(distance(p, a, b))

        smallest = min(candidates)

        if smallest > tolerance:
            break

        result.pop(candidates.index(smallest))

    return result

regions = []

while remaining:
    start = remaining.pop()
    queue = deque([start])
    region = [start]

    while queue:
        x, y = queue.popleft()

        for p in (
            (x+1,y), (x-1,y),
            (x,y+1), (x,y-1)
        ):
            if p in remaining:
                remaining.remove(p)
                queue.append(p)
                region.append(p)

    if len(region) >= 100:
        regions.append(region)

regions.sort(key=lambda r: min(x for x,y in r))

print("S-Eye: Geometric recognition")
print("Objects:", len(regions))

predictions = []

for number, region in enumerate(regions, 1):
    outline = hull(region)

    xs = [x for x,y in region]
    ys = [y for x,y in region]

    scale = max(
        max(xs)-min(xs)+1,
        max(ys)-min(ys)+1
    )

    corners = simplify(outline, scale * 0.04)
    count = len(corners)


    if count == 3:
        shape = "Triangle"

    elif count == 4:
        sides = []

        for i in range(4):
            a = corners[i]
            b = corners[(i + 1) % 4]

            sides.append(
                hypot(b[0]-a[0], b[1]-a[1])
            )

        ratio = min(sides) / max(sides)

        if ratio >= 0.95:
            shape = "Square-like"
        elif ratio >= 0.75:
            shape = "Ambiguous quadrilateral"
        else:
            shape = "Rectangle-like"

        print(
            f"  Side lengths: "
            f"{[round(s, 1) for s in sides]}, "
            f"ratio={ratio:.3f}"
        )

    elif count >= 5:
        shape = "Circle-like"

    else:
        shape = "Unknown"

    predictions.append(shape)

    print(
        f"Object {number}: {shape}, "
        f"corners={count}, "
        f"hull_vertices={len(outline)}"
    )

