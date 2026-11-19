from pathlib import Path

source = Path("geometry_v2_runner.py").read_text()

old = '''        if ratio >= 0.90:
            shape = "Square"
        else:
            shape = "Rectangle"'''

new = '''        if ratio >= 0.95:
            shape = "Square-like"
        elif ratio >= 0.75:
            shape = "Ambiguous quadrilateral"
        else:
            shape = "Rectangle-like"'''

if old not in source:
    raise SystemExit(
        "Expected classification block not found. "
        "No files changed."
    )

updated = source.replace(old, new, 1)

Path("geometry_v3_runner.py").write_text(updated)

print("S-Eye: Experimental classifier created")
print("Saved: geometry_v3_runner.py")
print("Original classifier preserved")
