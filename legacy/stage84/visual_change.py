from PIL import Image
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"

names = [
    "20261112_193338.jpg",
    "20261112_194129.jpg"
]

images = []

for name in names:
    with Image.open(folder / name) as photo:
        photo = photo.convert("RGB")
        photo = photo.resize((100, 100))
        images.append(list(photo.get_flattened_data()))

changed = 0
total_difference = 0

for first, second in zip(images[0], images[1]):
    difference = sum(
        abs(a - b) for a, b in zip(first, second)
    ) / 3

    total_difference += difference

    if difference > 30:
        changed += 1

total = len(images[0])

print("S-Eye: Visual comparison")
print("Pixels compared:", total)
print("Changed pixels:", changed)
print("Changed percentage:", round(changed / total * 100, 2))
print("Average pixel difference:", round(total_difference / total, 2))
