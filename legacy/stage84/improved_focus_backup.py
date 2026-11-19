from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"

def load(name):
    with Image.open(folder / name) as im:
        return im.convert("RGB").resize((100, 100))

before = load("20261112_194411.jpg")
after = load("20261112_194422.jpg")

a = before.filter(ImageFilter.GaussianBlur(1))
b = after.filter(ImageFilter.GaussianBlur(1))

mask = Image.new("L", (100, 100), 0)

for y in range(100):
    for x in range(100):
        p = a.getpixel((x, y))
        q = b.getpixel((x, y))

        difference = sum(abs(i-j) for i,j in zip(p,q)) / 3

        if difference > 25:
            mask.putpixel((x,y), 255)

mask = mask.filter(ImageFilter.MaxFilter(3))
mask = mask.filter(ImageFilter.MinFilter(3))

remaining = {
    (x,y)
    for y in range(100)
    for x in range(100)
    if mask.getpixel((x,y)) > 0
}

clusters = []

while remaining:
    start = remaining.pop()
    stack = [start]
    group = [start]

    while stack:
        x,y = stack.pop()

        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            point = (x+dx,y+dy)

            if point in remaining:
                remaining.remove(point)
                stack.append(point)
                group.append(point)

    if len(group) >= 15:
        clusters.append(group)

clusters.sort(key=len, reverse=True)

result = after.copy()
draw = ImageDraw.Draw(result)

for group in clusters:
    xs = [p[0] for p in group]
    ys = [p[1] for p in group]

    draw.rectangle(
        (min(xs),min(ys),max(xs),max(ys)),
        outline="red",
        width=1
    )

result.save("improved_focus.png")

print("S-Eye: Improved focus")
print("Regions:", len(clusters))
print("Largest region:", len(clusters[0]) if clusters else 0)
print("Saved: improved_focus.png")
