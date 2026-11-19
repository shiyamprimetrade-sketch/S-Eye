from PIL import Image, ImageDraw, ImageOps
from pathlib import Path
from collections import deque

camera = Path.home() / "storage/shared/DCIM/Camera"

photos = sorted(
    [
        p for p in camera.iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg")
    ],
    key=lambda p: p.stat().st_mtime
)

if not photos:
    raise SystemExit("No camera photos found")

photo = photos[-1]

image = ImageOps.exif_transpose(
    Image.open(photo)
).convert("RGB")

image.thumbnail((200, 200))

gray = image.convert("L")
pixels = gray.load()

remaining = {
    (x, y)
    for y in range(gray.height)
    for x in range(gray.width)
    if pixels[x, y] < 100
}

regions = []

while remaining:
    start = remaining.pop()
    queue = deque([start])
    region = [start]

    while queue:
        x, y = queue.popleft()

        for point in (
            (x+1, y),
            (x-1, y),
            (x, y+1),
            (x, y-1)
        ):
            if point in remaining:
                remaining.remove(point)
                queue.append(point)
                region.append(point)

    if len(region) >= 30:
        regions.append(region)

regions.sort(key=len, reverse=True)

draw = ImageDraw.Draw(image)

for i, region in enumerate(regions[:10], 1):
    xs = [x for x, y in region]
    ys = [y for x, y in region]

    box = (
        min(xs), min(ys),
        max(xs), max(ys)
    )

    draw.rectangle(box, outline="red", width=2)
    draw.text(
        (box[0] + 2, box[1] + 2),
        str(i),
        fill="yellow",
        stroke_width=1,
        stroke_fill="black"
    )

image.save("camera_regions.png")

print("S-Eye: Region visualization")
print("Photo:", photo.name)
print("Regions:", len(regions))
print("Saved: camera_regions.png")
