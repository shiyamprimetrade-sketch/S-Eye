#!/usr/bin/env python3
"""S-Eye Stage 58: versioned visual memory migration."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT / "visual_memory.jsonl"
NEW = ROOT / "visual_memory_v2.jsonl"
REPORT = ROOT / "s_eye_analysis.json"

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def find_photo(filename):
    candidates = [
        ROOT / filename,
        Path.home() / "storage/shared/DCIM/Camera" / filename,
    ]

    for path in candidates:
        if path.is_file():
            return path

    raise FileNotFoundError(
        f"Original photograph not found: {filename}"
    )

def main():
    print("S-Eye Stage 58 — Memory v2")

    old_records = [
        json.loads(line)
        for line in OLD.read_text().splitlines()
        if line.strip()
    ]

    if not old_records:
        raise ValueError("No source observations")

    current_report_hash = sha256(REPORT.read_bytes())
    report = json.loads(REPORT.read_text())

    if not report.get("success"):
        raise ValueError("Current report is not successful")

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
        raise ValueError("Processed image size missing")

    width, height = map(int, match.groups())

    if width <= 0 or height <= 0:
        raise ValueError("Invalid processed image size")

    upgraded = []

    for record in old_records:
        if record["report_sha256"] != current_report_hash:
            raise ValueError(
                "Historical report unavailable for verification. "
                "Migration stopped without overwriting memory."
            )

        photo = find_photo(record["photo"])
        photo_hash = sha256(photo.read_bytes())

        observation_id = sha256(
            (
                photo_hash + ":" +
                record["report_sha256"]
            ).encode()
        )[:24]

        objects = []

        for obj in record["objects"]:
            item = dict(obj)
            x1, y1, x2, y2 = item["bbox"]

            if not (
                0 <= x1 <= x2 < width
                and 0 <= y1 <= y2 < height
            ):
                raise ValueError(
                    f"Region {item['region_id']} outside image"
                )

            item["object_id"] = (
                f"{observation_id}:"
                f"{item['region_id']}"
            )

            objects.append(item)

        upgraded.append({
            **record,
            "schema_version": 2,
            "observation_id": observation_id,
            "photo_sha256": photo_hash,
            "processed_image_size": [width, height],
            "objects": objects,
            "object_count": len(objects),
        })

    # Write only after every record has passed validation.
    temporary = NEW.with_suffix(".jsonl.tmp")

    with temporary.open("w") as file:
        for record in upgraded:
            file.write(json.dumps(record) + "\n")

    # Verify the generated file before publishing it.
    loaded = [
        json.loads(line)
        for line in temporary.read_text().splitlines()
        if line.strip()
    ]

    if loaded != upgraded:
        raise ValueError("Migration verification failed")

    temporary.replace(NEW)

    print("Memory v2: CREATED AND VERIFIED")
    print("Observations:", len(upgraded))
    print(
        "Objects:",
        sum(r["object_count"] for r in upgraded)
    )
    print("Observation ID:", upgraded[0]["observation_id"])
    print("Photo SHA-256:", upgraded[0]["photo_sha256"])
    print("Saved:", NEW.name)
    print("Original memory preserved")

if __name__ == "__main__":
    main()
