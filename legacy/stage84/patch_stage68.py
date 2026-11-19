from pathlib import Path

path = Path("local_contrast.py")
source = path.read_text()

backup = Path("local_contrast_stage67_backup.py")

expected = '''from PIL import Image, ImageFilter, ImageOps
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
'''

replacement = '''from PIL import Image, ImageFilter, ImageOps
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
'''

if expected not in source:
    raise SystemExit(
        "Source structure differs from audited version. "
        "No changes made."
    )

if "Source SHA-256:" not in source:
    source = source.replace(
        'print("Photo:", photo.name)',
        'print("Photo:", photo.name)\n'
        'print("Source SHA-256:", photo_hash)',
        1
    )

updated = source.replace(expected, replacement, 1)

if not backup.exists():
    backup.write_text(path.read_text())

path.write_text(updated)

print("Stage 68: Explicit image selection installed")
print("Backup:", backup)
