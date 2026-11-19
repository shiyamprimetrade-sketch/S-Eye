from PIL import Image, ImageFilter
from collections import deque
from math import hypot

mask = Image.open("local_contrast_mask.png").convert("L")

grouped = mask.filter(ImageFilter.MaxFilter(9))
grouped = grouped.filter(ImageFilter.MinFilter(5))

remaining = {
    (x, y)
    for y in range(grouped.height)
    for x in range(grouped.width)
    if grouped.getpixel((x, y)) > 128
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
    return abs(cross(a, b, p)) / max(
        hypot(b[0]-a[0], b[1]-a[1]), 1e-9
    )

def simplify(poly, tolerance):
    result = poly[:]

    while len(result) > 3:
        errors = [
            distance(
                result[i],
                result[i-1],
                result[(i+1) % len(result)]
            )
            for i in range(len(result))
        ]

        smallest = min(errors)

        if smallest > tolerance:
            break

        result.pop(errors.index(smallest))

    return result

regions = []

while remaining:
    start = remaining.pop()
    queue = deque([start])
    region = [start]

    while queue:
        x, y = queue.popleft()

        for point in (
            (x+1,y), (x-1,y),
            (x,y+1), (x,y-1)
        ):
            if point in remaining:
                remaining.remove(point)
                queue.append(point)
                region.append(point)

    if len(region) >= 100:
        regions.append(region)

regions.sort(key=len, reverse=True)

print("S-Eye: Real-camera shape classification")

accepted = []

for region in regions:
    xs = [x for x,y in region]
    ys = [y for x,y in region]

    w = max(xs)-min(xs)+1
    h = max(ys)-min(ys)+1

    ratio = min(w,h)/max(w,h)

    if ratio >= 0.45:
        accepted.append(region)

print("Accepted regions:", len(accepted))

for i, region in enumerate(accepted, 1):
    outline = hull(region)

    xs = [x for x,y in region]
    ys = [y for x,y in region]

    scale = max(
        max(xs)-min(xs)+1,
        max(ys)-min(ys)+1
    )

    corners = simplify(outline, scale * 0.15)
    count = len(corners)

    if count == 3:
        shape = "Triangle"

    elif count == 4:
        sides = [
            hypot(
                corners[(j+1)%4][0]-corners[j][0],
                corners[(j+1)%4][1]-corners[j][1]
            )
            for j in range(4)
        ]

        ratio = min(sides)/max(sides)

        shape = (
            "Square" if ratio >= 0.90
            else "Rectangle"
        )

    elif count >= 5:
        shape = "Circle-like"

    else:
        shape = "Unknown"

    print(
        f"Region {i}: "
        f"{shape}, "
        f"corners={count}, "
        f"hull_vertices={len(outline)}"
    )
