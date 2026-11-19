import subprocess
import sys
import re

expected = [
    "Circle-like",
    "Square",
    "Square",
    "Rectangle",
    "Triangle",
    "Triangle"
]

result = subprocess.run(
    [sys.executable, "geometry_v2_runner.py"],
    capture_output=True,
    text=True
)

print(result.stdout)

if result.returncode != 0:
    print("ERROR:", result.stderr)
    sys.exit(1)

matches = re.findall(
    r"^Object \d+: ([A-Za-z-]+),",
    result.stdout,
    re.MULTILINE
)

print("Expected:", expected)
print("Detected:", matches)

passed = matches == expected

print("Stage 35:", "PASS" if passed else "FAIL")

sys.exit(0 if passed else 1)
