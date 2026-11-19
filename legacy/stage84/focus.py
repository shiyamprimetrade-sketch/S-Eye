from PIL import Image, ImageDraw
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"

before = folder / "20261112_194411.jpg"
after = folder / "20261112_194422.jpg"

def load(path):
    with Image.open(path) as im:
        return im.convert("RGB").resize((100, 100))

a = load(before)
b = load(after)

changed = []

for y in range(100):
    for x in range(100):
        p = a.getpixel((x, y))
        q = b.getpixel((x, y))

        difference = sum(abs(i-j) for i,j in zip(p,q)) / 3

        if difference > 30:
            changed.append((x,y))

if changed:
    left = min(x for x,y in changed)
    right = max(x for x,y in changed)
    top = min(y for x,y in changed)
    bottom = max(y for x,y in changed)

    print("S-Eye: Focus acquired")
    print("Changed pixels:", len(changed))
    print("Bounding box:", (left, top, right, bottom))

    draw = ImageDraw.Draw(b)
    draw.rectangle(
        (left, top, right, bottom),
        outline="red",
        width=2
    )

    b.save("focus_result.png")
    print("Saved: focus_result.png")
else:
    print("S-Eye: No significant change detected")
