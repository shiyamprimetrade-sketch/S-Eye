from PIL import Image
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"

names = [
    "20261112_194407.jpg",
    "20261112_194411.jpg",
    "20261112_194422.jpg"
]

def compare(a, b):
    images = []

    for name in (a, b):
        with Image.open(folder / name) as photo:
            photo = photo.convert("RGB").resize((100, 100))
            images.append(list(photo.get_flattened_data()))

    differences = [
        sum(abs(x-y) for x,y in zip(p,q)) / 3
        for p,q in zip(images[0], images[1])
    ]

    changed = sum(d > 30 for d in differences)

    return round(changed / len(differences) * 100, 2)

stationary = compare(names[0], names[1])
modified = compare(names[1], names[2])

print("S-Eye Reliability Test")
print("Stationary scene:", stationary, "% changed")
print("Modified scene:", modified, "% changed")
print("Difference:", round(modified-stationary, 2), "percentage points")

if modified > stationary:
    print("Result: Modified scene produced more visual changes")
else:
    print("Result: No increase detected; investigate conditions")
