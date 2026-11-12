from PIL import Image, ImageDraw, ImageFilter
from collections import deque

mask = Image.open(
    "local_contrast_mask.png"
).convert("L")

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

        for point in (
            (x+1, y), (x-1, y),
            (x, y+1), (x, y-1)
        ):
            if point in remaining:
                remaining.remove(point)
                queue.append(point)
                region.append(point)

    if len(region) >= 100:
        regions.append(region)

regions.sort(key=len, reverse=True)

output = Image.open(
    "local_contrast_mask.png"
).convert("RGB")

draw = ImageDraw.Draw(output)

accepted = 0
rejected = 0

print("S-Eye: Geometric region filtering")

for region in regions:
    xs = [x for x, y in region]
    ys = [y for x, y in region]

    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)

    width = x2 - x1 + 1
    height = y2 - y1 + 1

    ratio = min(width, height) / max(width, height)

    if ratio < 0.45:
        rejected += 1
        print(
            f"Rejected region: ratio={ratio:.3f}"
        )
        continue

    accepted += 1

    draw.rectangle(
        (x1, y1, x2, y2),
        outline="lime",
        width=2
    )

    draw.text(
        (x1, max(0, y1-12)),
        str(accepted),
        fill="yellow"
    )

    print(
        f"Accepted region {accepted}: "
        f"ratio={ratio:.3f}"
    )

output.save("filtered_shapes.png")

print("Accepted:", accepted)
print("Rejected:", rejected)
print("Saved: filtered_shapes.png")
