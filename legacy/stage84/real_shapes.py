from PIL import Image
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"
photos = list(folder.glob("*.jpg"))

if not photos:
    print("No photographs found")
    raise SystemExit

photo = max(photos, key=lambda p: p.stat().st_mtime)

with Image.open(photo) as im:
    gray = im.convert("L").resize((100, 100))

dark = [
    (x, y)
    for y in range(100)
    for x in range(100)
    if gray.getpixel((x, y)) < 100
]

if not dark:
    print("No dark regions detected")
    raise SystemExit

left = min(x for x, y in dark)
right = max(x for x, y in dark)
top = min(y for x, y in dark)
bottom = max(y for x, y in dark)

width = right - left + 1
height = bottom - top + 1
fill = len(dark) / (width * height)

print("S-Eye: Real shape experiment")
print("Photo:", photo.name)
print("Dark pixels:", len(dark))
print("Bounding box:", (left, top, right, bottom))
print("Fill ratio:", round(fill, 3))
