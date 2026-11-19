from PIL import Image
from pathlib import Path

folder = Path.home() / "storage/shared/DCIM/Camera"

photos = list(folder.glob("*.jpg"))

if not photos:
    print("S-Eye: No photographs found")
    exit()

photo = max(photos, key=lambda p: p.stat().st_mtime)

with Image.open(photo) as image:
    image = image.convert("RGB")
    image.thumbnail((100, 100))

    pixels = list(image.get_flattened_data())

    red = sum(p[0] for p in pixels) // len(pixels)
    green = sum(p[1] for p in pixels) // len(pixels)
    blue = sum(p[2] for p in pixels) // len(pixels)

    light = (red + green + blue) // 3

    if light < 50:
        vision = "Dark"
    elif light < 160:
        vision = "Dim"
    else:
        vision = "Bright"

    print("S-Eye: I received an image")
    print("Photo:", photo.name)
    print("Light:", light)
    print("Vision:", vision)
    print("Average RGB:", red, green, blue)

colors = {"Red": red, "Green": green, "Blue": blue}
dominant = max(colors, key=colors.get)

if max(colors.values()) - min(colors.values()) < 20:
    dominant = "Neutral / Gray"

print("Dominant color:", dominant)

def detect_edges(image):
    gray = image.convert("L")
    width, height = gray.size
    edges = 0

    for y in range(height - 1):
        for x in range(width - 1):
            current = gray.getpixel((x, y))
            right = gray.getpixel((x + 1, y))
            below = gray.getpixel((x, y + 1))

            if abs(current - right) > 30:
                edges += 1
            if abs(current - below) > 30:
                edges += 1

    return edges

print("Detected edges:", detect_edges(image))

def locate_edges(image):
    gray = image.convert("L")
    w, h = gray.size
    regions = {"Top": 0, "Bottom": 0,
               "Left": 0, "Right": 0}

    for y in range(h - 1):
        for x in range(w - 1):
            a = gray.getpixel((x, y))
            b = gray.getpixel((x + 1, y))

            if abs(a - b) > 30:
                regions["Top" if y < h/2 else "Bottom"] += 1
                regions["Left" if x < w/2 else "Right"] += 1

    return regions

areas = locate_edges(image)
print("Visual regions:", areas)
print("Most active region:", max(areas, key=areas.get))

import json
from datetime import datetime

observation = {
    "time": datetime.now().isoformat(timespec="seconds"),
    "photo": photo.name,
    "brightness": light,
    "vision": vision,
    "rgb": [red, green, blue],
    "dominant_color": dominant,
    "edge_count": detect_edges(image),
    "regions": areas
}

with open("eye_memory.jsonl", "a") as memory:
    memory.write(json.dumps(observation) + "\n")

print("S-Eye: Observation saved")
print("Total memories:", sum(1 for line in open("eye_memory.jsonl")))
