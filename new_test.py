from PIL import Image, ImageDraw

im = Image.new("RGB", (600, 400), "white")
d = ImageDraw.Draw(im)

d.ellipse((20, 20, 100, 100), fill="black")
d.rectangle((200, 20, 280, 100), fill="black")
d.polygon([(450, 20), (400, 110), (500, 110)], fill="black")

d.rectangle((20, 220, 140, 280), fill="black")
d.ellipse((220, 200, 320, 300), fill="black")
d.polygon([(450, 200), (400, 310), (500, 310)], fill="black")

im.save("paperless_shapes.png")
print("Generated six unfamiliar test shapes")
