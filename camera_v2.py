from pathlib import Path

source = Path("classify_camera.py").read_text()

# Use the previously tested simplification tolerance.
old_tolerance = "scale * 0.04"
if old_tolerance not in source:
    raise SystemExit("Original tolerance not found")

source = source.replace(
    old_tolerance,
    "scale * 0.08",
    1
)

old = '''        shape = (
            "Square" if ratio >= 0.90
            else "Rectangle"
        )'''

new = '''        if ratio >= 0.95:
            shape = "Square-like"
        elif ratio >= 0.75:
            shape = "Ambiguous quadrilateral"
        else:
            shape = "Rectangle-like"'''

if old not in source:
    raise SystemExit("Original classification block not found")

source = source.replace(old, new, 1)

Path("classify_camera_v2.py").write_text(source)

print("S-Eye: Camera classifier v2 created")
print("Original classifier preserved")
