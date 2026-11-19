from pathlib import Path
import subprocess
import sys
import re

source = Path("classify_camera.py").read_text()

expected = [
    "Circle-like",
    "Square",
    "Triangle"
]

tolerances = [
    0.04,
    0.06,
    0.08,
    0.10,
    0.12,
    0.15
]

print("S-Eye: Corner tolerance experiment")
print("Expected:", expected)
print()

for tolerance in tolerances:
    modified = source.replace(
        "scale * 0.04",
        f"scale * {tolerance}"
    )

    Path("tolerance_runner.py").write_text(modified)

    result = subprocess.run(
        [sys.executable, "tolerance_runner.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            f"Tolerance {tolerance:.2f}: ERROR",
            result.stderr
        )
        continue

    matches = re.findall(
        r"^Region \d+: ([A-Za-z-]+),",
        result.stdout,
        re.MULTILINE
    )

    correct = sum(
        actual == target
        for actual, target in zip(matches, expected)
    ) if len(matches) == len(expected) else 0

    print(
        f"Tolerance {tolerance:.2f}: "
        f"{matches} — {correct}/3 correct"
    )

print()
print("Original classify_camera.py preserved")
