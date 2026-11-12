def eye(pixels):
    light = sum(pixels) // len(pixels)
    if light < 50:
        return "Dark"
    if light < 160:
        return "Dim"
    return "Bright"

print("S-Eye:", eye([0, 100, 255]))
