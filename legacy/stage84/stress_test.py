from PIL import Image, ImageDraw
from pathlib import Path
import subprocess
import sys
import re

source = Path("geometry_v2_runner.py").read_text()

runner = source.replace(
    '"geometry_challenge.png"',
    '"stress_input.png"'
)

Path("stress_runner.py").write_text(
    runner
)

cases = []

for shape in ["Circle", "Square", "Rectangle", "Triangle"]:
    for angle in [0, 15, 30, 45, 60]:
        cases.append((shape, angle))

results = []

for shape, angle in cases:
    canvas = Image.new("RGB", (300, 300), "white")

    layer = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    if shape == "Circle":
        draw.ellipse((40, 40, 120, 120), fill="black")

    elif shape == "Square":
        draw.rectangle((40, 40, 120, 120), fill="black")

    elif shape == "Rectangle":
        draw.rectangle((20, 50, 140, 110), fill="black")

    elif shape == "Triangle":
        draw.polygon(
            [(80, 20), (20, 140), (140, 140)],
            fill="black"
        )

    rotated = layer.rotate(
        angle,
        expand=True,
        resample=Image.Resampling.NEAREST
    )

    canvas.paste(
        rotated,
        (
            (300 - rotated.width) // 2,
            (300 - rotated.height) // 2
        ),
        rotated
    )

    canvas.save("stress_input.png")

    process = subprocess.run(
        [sys.executable, "stress_runner.py"],
        capture_output=True,
        text=True
    )

    matches = re.findall(
        r"^Object \d+: ([A-Za-z-]+),",
        process.stdout,
        re.MULTILINE
    )

    expected = "Circle-like" if shape == "Circle" else shape

    detected = matches[0] if len(matches) == 1 else "Detection-error"

    passed = (
        process.returncode == 0
        and len(matches) == 1
        and detected == expected
    )

    results.append(passed)

    print(
        f"{shape:10} angle={angle:2} "
        f"detected={detected:15} "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print("S-Eye Stress Test")
print("Passed:", sum(results))
print("Total:", len(results))
print("Accuracy:", round(100 * sum(results) / len(results), 1), "%")
