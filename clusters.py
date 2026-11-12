from PIL import Image, ImageDraw
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"

def load(name):
    with Image.open(folder / name) as im:
        return im.convert("RGB").resize((100, 100))

a = load("20261112_194411.jpg")
b = load("20261112_194422.jpg")

changed = set()

for y in range(100):
    for x in range(100):
        p = a.getpixel((x, y))
        q = b.getpixel((x, y))
        difference = sum(abs(i-j) for i,j in zip(p,q)) / 3
        if difference > 30:
            changed.add((x,y))

remaining = changed.copy()
clusters = []

while remaining:
    start = remaining.pop()
    stack = [start]
    cluster = [start]

    while stack:
        x,y = stack.pop()

        for neighbor in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if neighbor in remaining:
                remaining.remove(neighbor)
                stack.append(neighbor)
                cluster.append(neighbor)

    if len(cluster) >= 5:
        clusters.append(cluster)

clusters.sort(key=len, reverse=True)

draw = ImageDraw.Draw(b)

for cluster in clusters[:5]:
    xs = [p[0] for p in cluster]
    ys = [p[1] for p in cluster]
    box = (min(xs), min(ys), max(xs), max(ys))
    draw.rectangle(box, outline="red", width=1)

b.save("clusters_result.png")

print("S-Eye: Cluster analysis")
print("Changed pixels:", len(changed))
print("Clusters found:", len(clusters))
print("Largest cluster:", len(clusters[0]) if clusters else 0)
print("Saved: clusters_result.png")
