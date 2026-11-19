from PIL import Image
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"
photo = folder / "20261112_200137.jpg"

with Image.open(photo) as im:
    image = im.convert("L").resize((100, 100))

mask = image.point(lambda p: 255 if p < 100 else 0)
mask = mask.resize((500, 500), Image.Resampling.NEAREST)

mask.save("shape_mask.png")

print("S-Eye: Diagnostic mask created")
print("Source:", photo.name)
print("Threshold: 100")
print("Saved: shape_mask.png")
