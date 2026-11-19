from pathlib import Path
from math import hypot

source = Path("geometry_challenge_runner.py").read_text()

start = source.index('    if count == 3:')
end = source.index('    predictions.append(shape)', start)

replacement = '''
    if count == 3:
        shape = "Triangle"

    elif count == 4:
        sides = []

        for i in range(4):
            a = corners[i]
            b = corners[(i + 1) % 4]

            sides.append(
                hypot(b[0]-a[0], b[1]-a[1])
            )

        ratio = min(sides) / max(sides)

        if ratio >= 0.90:
            shape = "Square"
        else:
            shape = "Rectangle"

        print(
            f"  Side lengths: "
            f"{[round(s, 1) for s in sides]}, "
            f"ratio={ratio:.3f}"
        )

    elif count >= 5:
        shape = "Circle-like"

    else:
        shape = "Unknown"

'''

updated = source[:start] + replacement + source[end:]

Path("geometry_v2_runner.py").write_text(updated)

print("Created geometry_v2_runner.py")
print("Original geometry.py preserved")
