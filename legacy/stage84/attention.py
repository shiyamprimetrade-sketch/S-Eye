from PIL import Image
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"

before = "20261112_194411.jpg"
after = "20261112_194422.jpg"

def read(name):
    with Image.open(folder / name) as photo:
        return list(
            photo.convert("RGB")
            .resize((100, 100))
            .get_flattened_data()
        )

a = read(before)
b = read(after)

regions = {
    "Top Left": 0,
    "Top Right": 0,
    "Bottom Left": 0,
    "Bottom Right": 0
}

for i, (p, q) in enumerate(zip(a, b)):
    difference = sum(abs(x-y) for x, y in zip(p, q)) / 3

    if difference > 30:
        x = i % 100
        y = i // 100

        vertical = "Top" if y < 50 else "Bottom"
        horizontal = "Left" if x < 50 else "Right"

        regions[vertical + " " + horizontal] += 1

print("S-Eye: Visual attention")
print("Changed pixels by region:")

for name, count in regions.items():
    print(name + ":", count)

print("Attention target:", max(regions, key=regions.get))
print("Total changed:", sum(regions.values()))
