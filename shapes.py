from PIL import Image
from pathlib import Path

image = Image.open("improved_focus.png")

print("S-Eye: Shape analysis")
print("Image dimensions:", image.size)

# Analyze the visually confirmed central region
left, top, right, bottom = 30, 38, 43, 58

width = right - left
height = bottom - top

ratio = width / height

if 0.85 <= ratio <= 1.15:
    shape = "Square-like"
elif ratio < 0.85:
    shape = "Vertical rectangle-like"
else:
    shape = "Horizontal rectangle-like"

print("Region width:", width)
print("Region height:", height)
print("Aspect ratio:", round(ratio, 2))
print("Shape:", shape)
