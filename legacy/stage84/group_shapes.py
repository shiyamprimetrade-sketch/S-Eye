from PIL import Image, ImageFilter, ImageDraw
from collections import deque

mask = Image.open(
    "local_contrast_mask.png"
).convert("L")

# Connect nearby fragments of pencil strokes.
grouped = mask.filter(ImageFilter.MaxFilter(9))
grouped = grouped.filter(ImageFilter.MinFilter(5))

pixels = grouped.load()

remaining = {
    (x, y)
    for y in range(grouped.height)
    for x in range(grouped.width)
    if pixels[x, y] > 128
}

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

regions.sort(key=len, reverse=True)

output = Image.open(
    "local_contrast_mask.png"
).convert("RGB")

draw = ImageDraw.Draw(output)

print("S-Eye: Grouped shape regions")
print("Regions:", len(regions))

for i, region in enumerate(regions, 1):
    xs = [x for x,y in region]
    ys = [y for x,y in region]

    box = (
        min(xs), min(ys),
        max(xs), max(ys)
    )

    draw.rectangle(
        box,
        outline="red",
        width=2
    )

    draw.text(
        (box[0], max(0, box[1]-12)),
        str(i),
        fill="yellow"
    )

    print(
        f"Region {i}: "
        f"pixels={len(region)}, "
        f"box={box}"
    )

output.save("grouped_shapes.png")
print("Saved: grouped_shapes.png")
