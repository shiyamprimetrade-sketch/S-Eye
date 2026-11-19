from PIL import Image, ImageDraw

image = Image.new("RGB", (600, 250), "white")
draw = ImageDraw.Draw(image)

# Circle
draw.ellipse((30, 65, 130, 165), fill="black")

# Square rotated 45 degrees
draw.polygon(
    [(270, 40), (320, 90), (270, 140), (220, 90)],
    fill="black"
)

# Triangle rotated sideways
draw.polygon(
    [(440, 40), (440, 160), (550, 100)],
    fill="black"
)

image.save("rotation_shapes.png")

print("S-Eye: Rotation challenge generated")
print("Shapes: Circle, Rotated Square, Sideways Triangle")
print("Saved: rotation_shapes.png")
