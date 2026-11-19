from PIL import Image, ImageDraw

im = Image.new("RGB", (700, 400), "white")
d = ImageDraw.Draw(im)

# Different-sized circle
d.ellipse((20, 20, 90, 90), fill="black")

# Unrotated square
d.rectangle((170, 20, 270, 120), fill="black")

# Triangle pointing upward
d.polygon(
    [(410, 20), (350, 130), (470, 130)],
    fill="black"
)

# Another rotated square
d.polygon(
    [(90, 220), (150, 280),
     (90, 340), (30, 280)],
    fill="black"
)

# Wide rectangle
d.rectangle((230, 240, 390, 310), fill="black")

# Triangle pointing downward
d.polygon(
    [(540, 220), (660, 220), (600, 350)],
    fill="black"
)

im.save("geometry_challenge.png")
print("Generated six geometry challenge shapes")
