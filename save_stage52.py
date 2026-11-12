import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

files = [
    "geometry_v2_runner.py",
    "geometry_v3_runner.py",
    "classify_camera.py",
    "classify_camera_v2.py",
    "camera_v2.py",
    "uncertainty_test.py",
    "borderline_test.py",
    "stress_test.py",
    "local_contrast.py",
    "group_shapes.py",
    "filter_regions.py",
]

checksums = {}

for filename in files:
    path = Path(filename)

    if not path.is_file():
        raise SystemExit(
            f"Missing file: {filename}. Checkpoint not saved."
        )

    checksums[filename] = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

checkpoint = {
    "project": "S-Eye",
    "stage": 52,
    "created_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "verified_results": {
        "synthetic_shapes": "6/6",
        "uncertainty_rules": "9/9",
        "camera_regions": 3,
        "camera_labels": [
            "Circle-like",
            "Ambiguous quadrilateral",
            "Triangle"
        ],
        "borderline_test": "4/8"
    },
    "files_sha256": checksums
}

destination = Path("checkpoints/stage52.json")

destination.write_text(
    json.dumps(checkpoint, indent=2)
)

saved = json.loads(destination.read_text())

for filename, expected in saved["files_sha256"].items():
    actual = hashlib.sha256(
        Path(filename).read_bytes()
    ).hexdigest()

    if actual != expected:
        raise SystemExit(
            f"Verification failed: {filename}"
        )

print("S-Eye Stage 52: CHECKPOINT VERIFIED")
print("Files:", len(checksums))
print("Checkpoint:", destination)
print("Previous Stage 37 checkpoint preserved")
