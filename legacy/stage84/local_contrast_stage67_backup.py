from PIL import Image, ImageFilter, ImageOps
from pathlib import Path

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

image.thumbnail((300, 400))

gray = image.convert("L")

# Estimate slowly changing background illumination
background = gray.filter(
    ImageFilter.GaussianBlur(radius=15)
)

original = gray.load()
blurred = background.load()

mask = Image.new("L", gray.size, 0)
output = mask.load()

threshold = 18

for y in range(gray.height):
    for x in range(gray.width):
        difference = blurred[x, y] - original[x, y]

        if difference > threshold:
            output[x, y] = 255

mask.save("local_contrast_mask.png")

print("S-Eye: Local contrast segmentation")
print("Photo:", photo.name)
print("Image size:", gray.size)
print("Contrast threshold:", threshold)
print("Saved: local_contrast_mask.png")
