from PIL import Image, ImageFilter, ImageOps
from pathlib import Path
import argparse
import hashlib

parser = argparse.ArgumentParser(
    description="S-Eye local contrast segmentation"
)

parser.add_argument(
    "--image",
    type=Path,
    help="Explicit photograph path"
)

args = parser.parse_args()

if args.image is not None:
    photo = args.image.expanduser().resolve()

    if not photo.is_file():
        parser.error(
            f"Specified photograph does not exist: {photo}"
        )

    if photo.suffix.lower() not in (
        ".jpg", ".jpeg", ".png"
    ):
        parser.error("Unsupported image format")

else:
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

photo_hash = hashlib.sha256(
    photo.read_bytes()
).hexdigest()

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
print("Source SHA-256:", photo_hash)
print("Image size:", gray.size)
print("Contrast threshold:", threshold)
print("Saved: local_contrast_mask.png")
