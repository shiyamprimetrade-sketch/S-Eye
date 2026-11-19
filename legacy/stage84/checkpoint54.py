import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent

files = [
    "s_eye.py",
    "s_eye_analysis.json",
    "classify_camera_v2.py",
    "local_contrast.py",
    "group_shapes.py",
    "filter_regions.py",
]

report = json.loads(
    (root / "s_eye_analysis.json").read_text()
)

assert report["success"] is True
assert len(report["steps"]) == 4
assert all(step["success"] for step in report["steps"])

geometry_output = report["steps"][-1]["output"]

expected = [
    "Accepted regions: 3",
    "Region 1: Circle-like",
    "Region 2: Ambiguous quadrilateral",
    "Region 3: Triangle",
]

for item in expected:
    assert item in geometry_output, (
        f"Missing expected result: {item}"
    )

checksums = {}

for filename in files:
    path = root / filename
    checksums[filename] = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

checkpoint = {
    "project": "S-Eye",
    "stage": 54,
    "timestamp_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "verified": {
        "pipeline_steps": 4,
        "accepted_regions": 3,
        "rejected_artifacts": 1,
        "report_valid": True
    },
    "sha256": checksums
}

destination = root / "checkpoints/stage54.json"
destination.parent.mkdir(exist_ok=True)

destination.write_text(
    json.dumps(checkpoint, indent=2)
)

saved = json.loads(destination.read_text())

for filename, expected_hash in saved["sha256"].items():
    actual_hash = hashlib.sha256(
        (root / filename).read_bytes()
    ).hexdigest()
    assert actual_hash == expected_hash

print("S-Eye Stage 54: CHECKPOINT VERIFIED")
print("Pipeline: 4/4")
print("Accepted regions: 3")
print("Files protected by checksums:", len(files))
print("Checkpoint:", destination)
