from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import json
import hashlib

ROOT = Path(__file__).resolve().parent
CAMERA = Path.home() / "storage/shared/DCIM/Camera"
OUT = ROOT / "stage82_dataset"
OUT.mkdir(exist_ok=True)

photos = sorted(
    CAMERA.glob("20261112_*.jpg")
)

if not photos:
    raise SystemExit("No matching photographs found")

width, height = 320, 280
columns = 2
rows = (len(photos) + columns - 1) // columns

sheet = Image.new(
    "RGB",
    (columns * width, rows * height),
    "white"
)

draw = ImageDraw.Draw(sheet)
manifest = []

for number, photo in enumerate(photos, 1):
    with Image.open(photo) as original:
        image = ImageOps.exif_transpose(original)
        image.thumbnail((300, 235))
        thumbnail = image.convert("RGB")

    x = ((number - 1) % columns) * width
    y = ((number - 1) // columns) * height

    sheet.paste(
        thumbnail,
        (
            x + (width - thumbnail.width) // 2,
            y + 5
        )
    )

    draw.text(
        (x + 10, y + 245),
        f"{number}: {photo.name}",
        fill="black"
    )

    manifest.append({
        "number": number,
        "filename": photo.name,
        "sha256": hashlib.sha256(
            photo.read_bytes()
        ).hexdigest(),
        "ground_truth": None,
        "reviewed": False
    })

sheet_path = OUT / "contact_sheet.jpg"
manifest_path = OUT / "manifest.json"

sheet.save(sheet_path, quality=90)

manifest_path.write_text(
    json.dumps(manifest, indent=2)
)

print("S-Eye Stage 82: CONTACT SHEET CREATED")
print("Photographs:", len(manifest))
print("Contact sheet:", sheet_path)
print("Manifest:", manifest_path)
print("Ground-truth labels: NOT YET ASSIGNED")
print("Original photographs unchanged")
