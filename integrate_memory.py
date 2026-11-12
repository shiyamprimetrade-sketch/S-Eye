#!/usr/bin/env python3
"""S-Eye Stage 60: safe visual-memory integration."""

import hashlib
import json
import re
from pathlib import Path

from upgrade_memory_v2 import find_photo
from visual_memory import build_record

ROOT = Path(__file__).resolve().parent
MEMORY = ROOT / "visual_memory_v2.jsonl"
REPORT = ROOT / "s_eye_analysis.json"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def remember():
    report = json.loads(REPORT.read_text())

    if not report.get("success"):
        raise ValueError("Analysis did not succeed")

    record = build_record()
    photo = find_photo(record["photo"])

    current_hash = digest(photo.read_bytes())

    observation_id = digest(
        (
            current_hash + ":" +
            record["report_sha256"]
        ).encode()
    )[:24]

    segmentation = next(
        step["output"]
        for step in report["steps"]
        if step["script"] == "local_contrast.py"
    )

    match = re.search(
        r"Image size: \((\d+), (\d+)\)",
        segmentation
    )

    if not match:
        raise ValueError("Image dimensions missing")

    width, height = map(int, match.groups())

    for obj in record["objects"]:
        x1, y1, x2, y2 = obj["bbox"]

        if not (
            0 <= x1 <= x2 < width
            and 0 <= y1 <= y2 < height
        ):
            raise ValueError("Invalid bounding box")

        obj["object_id"] = (
            f"{observation_id}:{obj['region_id']}"
        )

    record.update({
        "schema_version": 2,
        "observation_id": observation_id,
        "photo_sha256": current_hash,
        "processed_image_size": [width, height],
    })

    existing = []

    if MEMORY.exists():
        existing = [
            json.loads(line)
            for line in MEMORY.read_text().splitlines()
            if line.strip()
        ]

    # Validate existing memory before any duplicate decision.
    from verify_memory_v2 import verify, resolve_photo

    errors = verify(existing, resolve_photo)

    if errors:
        raise ValueError(
            "Existing memory verification failed: "
            + "; ".join(errors)
        )

    # Stage 61 policy: one stored observation per image hash.
    # Previous duplicate records are retained for audit history.
    matching = [
        item for item in existing
        if item.get("photo_sha256") == current_hash
    ]

    if matching:
        print("S-Eye: Photograph already remembered")
        print("Photo SHA-256:", current_hash)
        print("Existing observations:", len(matching))
        print("No new memory record created")
        return

    # Preserve existing memory if writing fails.
    updated = existing + [record]

    temporary = MEMORY.with_suffix(".jsonl.tmp")

    with temporary.open("w") as file:
        for item in updated:
            file.write(json.dumps(item) + "\n")

    checked = [
        json.loads(line)
        for line in temporary.read_text().splitlines()
        if line.strip()
    ]

    if checked != updated:
        temporary.unlink(missing_ok=True)
        raise ValueError("Memory write verification failed")

    temporary.replace(MEMORY)

    print("S-Eye: Visual memory updated")
    print("Observation ID:", observation_id)
    print("Objects:", record["object_count"])
    print("Total observations:", len(updated))
    print("Memory:", MEMORY.name)

if __name__ == "__main__":
    remember()
