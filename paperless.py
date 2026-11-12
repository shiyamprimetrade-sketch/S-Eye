from PIL import Image, ImageDraw

image = Image.new("RGB", (600, 200), "white")
draw = ImageDraw.Draw(image)

draw.ellipse((30, 50, 130, 150), fill="black")
draw.rectangle((240, 50, 340, 150), fill="black")
draw.polygon(
    [(500, 40), (440, 150), (560, 150)],
    fill="black"
)

image.save("paperless_shapes.png")

print("S-Eye: Paperless experiment")
print("Generated: Circle, Square, Triangle")
print("Saved: paperless_shapes.png")
