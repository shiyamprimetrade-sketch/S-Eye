from PIL import Image, ImageOps
from collections import deque
from pathlib import Path

camera = Path.home() / "storage/shared/DCIM/Camera"

photos = sorted(
    [p for p in camera.iterdir()
     if p.suffix.lower() in (".jpg", ".jpeg")],
    key=lambda p: p.stat().st_mtime
)

if not photos:
    raise SystemExit("No camera photographs found")

photo = photos[-1]

image = Image.open(photo)
image = ImageOps.exif_transpose(image)
image.thumbnail((200, 200))

gray = image.convert("L")
pixels = gray.load()

threshold = 100

remaining = {
    (x, y)
    for y in range(gray.height)
    for x in range(gray.width)
    if pixels[x, y] < threshold
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

    if len(region) >= 30:
        regions.append(region)

regions.sort(key=len, reverse=True)

print("S-Eye: Real Camera Geometry")
print("Photo:", photo.name)
print("Image size:", gray.size)
print("Threshold:", threshold)
print("Dark regions:", len(regions))

for i, region in enumerate(regions[:10], 1):
    xs = [p[0] for p in region]
    ys = [p[1] for p in region]

    box = (
        min(xs), min(ys),
        max(xs), max(ys)
    )

    print(
        f"Region {i}: "
        f"pixels={len(region)}, "
        f"box={box}"
    )
