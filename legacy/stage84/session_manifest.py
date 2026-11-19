#!/usr/bin/env python3
"""S-Eye Stage 64: analysis provenance manifest."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "s_eye_analysis.json"
SESSIONS = ROOT / "sessions"

SCRIPTS = [
    "local_contrast.py",
    "group_shapes.py",
    "filter_regions.py",
    "classify_camera_v2.py",
]

OUTPUTS = [
    "local_contrast_mask.png",
    "grouped_shapes.png",
    "filtered_shapes.png",
]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    report = json.loads(REPORT.read_text())

    if not report.get("success"):
        raise SystemExit("FAIL: Analysis was unsuccessful")

    steps = report.get("steps", [])

    if len(steps) != len(SCRIPTS):
        raise SystemExit("FAIL: Unexpected pipeline length")

    for step, expected in zip(steps, SCRIPTS):
        if (
            step.get("script") != expected
            or not step.get("success")
        ):
            raise SystemExit("FAIL: Pipeline mismatch")

    from upgrade_memory_v2 import find_photo

    segmentation = steps[0]["output"]

    import re
    match = re.search(
        r"^Photo: (.+)$",
        segmentation,
        re.MULTILINE
    )

    if not match:
        raise SystemExit("FAIL: Photo name missing")

    photo = find_photo(match.group(1).strip())

    paths = [photo, REPORT]

    for name in SCRIPTS + OUTPUTS:
        path = ROOT / name

        if not path.is_file():
            raise SystemExit(f"FAIL: Missing {name}")

        paths.append(path)

    fingerprints = {}

    for path in paths:
        key = (
            f"photo/{path.name}"
            if path == photo
            else path.name
        )

        fingerprints[key] = {
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }

    session_id = hashlib.sha256(
        (
            fingerprints[f"photo/{photo.name}"]["sha256"]
            + fingerprints[REPORT.name]["sha256"]
        ).encode()
    ).hexdigest()[:24]

    manifest = {
        "schema_version": 1,
        "project": "S-Eye",
        "stage": 64,
        "session_id": session_id,
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_photo": photo.name,
        "pipeline_success": True,
        "files": fingerprints,
        "provenance_scope": (
            "Post-analysis snapshot; files were not isolated "
            "or hashed between pipeline stages."
        ),
    }

    SESSIONS.mkdir(exist_ok=True)

    destination = SESSIONS / f"{session_id}.json"

    if destination.exists():
        existing = json.loads(destination.read_text())

        if existing["files"] != fingerprints:
            raise SystemExit(
                "FAIL: Existing session fingerprint conflict"
            )

        print("S-Eye: Session already recorded")
    else:
        destination.write_text(
            json.dumps(manifest, indent=2)
        )
        print("S-Eye: Session manifest created")

    print("Session ID:", session_id)
    print("Files fingerprinted:", len(fingerprints))
    print("Manifest:", destination)

if __name__ == "__main__":
    main()
