from PIL import Image

image = Image.open("rotation_shapes.png").convert("L")

def foreground(x, y):
    if 0 <= x < image.width and 0 <= y < image.height:
        return image.getpixel((x, y)) < 128
    return False

# Find connected objects using the existing threshold
from collections import deque

remaining = {
    (x, y)
    for y in range(image.height)
    for x in range(image.width)
    if foreground(x, y)
}

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

regions.sort(key=lambda r: min(x for x,y in r))

for number, region in enumerate(regions, 1):
    points = set(region)

    boundary = [
        (x,y) for x,y in region
        if any(
            (x+dx,y+dy) not in points
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))
        )
    ]

    print(
        "Object", number,
        "boundary pixels:", len(boundary)
    )
