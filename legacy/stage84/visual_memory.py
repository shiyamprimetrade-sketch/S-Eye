#!/usr/bin/env python3
"""S-Eye Stage 55: structured visual observations."""

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "s_eye_analysis.json"
MEMORY = ROOT / "visual_memory.jsonl"

REGION_PATTERN = re.compile(
    r"^Region (\d+): (.+?), "
    r"corners=(\d+), hull_vertices=(\d+)$"
)

BOX_PATTERN = re.compile(
    r"^Region (\d+): pixels=(\d+), "
    r"box=\((\d+), (\d+), (\d+), (\d+)\)$"
)

def build_record():
    report = json.loads(REPORT.read_text())

    if not report.get("success"):
        raise ValueError("Pipeline report was not successful")

    steps = {
        step["script"]: step
        for step in report["steps"]
    }

    required = [
        "local_contrast.py",
        "group_shapes.py",
        "filter_regions.py",
        "classify_camera_v2.py",
    ]

    for script in required:
        if script not in steps or not steps[script]["success"]:
            raise ValueError(f"Missing successful step: {script}")

    segmentation = steps["local_contrast.py"]["output"]
    grouping = steps["group_shapes.py"]["output"]
    classification = steps["classify_camera_v2.py"]["output"]

    photo_match = re.search(
        r"^Photo: (.+)$",
        segmentation,
        re.MULTILINE
    )

    if not photo_match:
        raise ValueError("Photo identifier not found")

    photo_name = photo_match.group(1).strip()

    boxes = {}

    for line in grouping.splitlines():
        match = BOX_PATTERN.match(line)

        if match:
            region, pixels, x1, y1, x2, y2 = map(
                int, match.groups()
            )

            boxes[region] = {
                "pixels": pixels,
                "bbox": [x1, y1, x2, y2]
            }

    objects = []

    for line in classification.splitlines():
        match = REGION_PATTERN.match(line)

        if not match:
            continue

        region = int(match.group(1))
        label = match.group(2)
        corners = int(match.group(3))
        hull_vertices = int(match.group(4))

        if region not in boxes:
            raise ValueError(
                f"Missing bounding box for region {region}"
            )

        objects.append({
            "region_id": region,
            "label": label,
            "uncertain": (
                "Ambiguous" in label
                or label.endswith("-like")
            ),
            "corners": corners,
            "hull_vertices": hull_vertices,
            **boxes[region]
        })

    if not objects:
        raise ValueError("No classified objects found")

    expected_count = re.search(
        r"Accepted regions: (\d+)",
        classification
    )

    if not expected_count:
        raise ValueError("Accepted-region count missing")

    if len(objects) != int(expected_count.group(1)):
        raise ValueError("Object count mismatch")

    # Identify the source report without duplicating its contents.
    report_hash = hashlib.sha256(
        REPORT.read_bytes()
    ).hexdigest()

    return {
        "schema_version": 1,
        "project": "S-Eye",
        "source": "camera_pipeline",
        "photo": photo_name,
        "observed_at_utc": report["timestamp_utc"],
        "recorded_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "report_sha256": report_hash,
        "objects": objects,
        "object_count": len(objects),
        "verified_ground_truth": False
    }

def save():
    record = build_record()

    # Prevent duplicate writes for the same pipeline report.
    if MEMORY.exists():
        for line in MEMORY.read_text().splitlines():
            if not line.strip():
                continue

            previous = json.loads(line)

            if (
                previous.get("report_sha256")
                == record["report_sha256"]
            ):
                print("S-Eye: Observation already recorded")
                print("Objects:", previous["object_count"])
                return

    with MEMORY.open("a") as file:
        file.write(json.dumps(record) + "\n")

    print("S-Eye: Visual observation saved")
    print("Photo:", record["photo"])
    print("Objects:", record["object_count"])

    for obj in record["objects"]:
        print(
            f"Region {obj['region_id']}: "
            f"{obj['label']}, "
            f"uncertain={obj['uncertain']}, "
            f"bbox={obj['bbox']}"
        )

    print("Memory:", MEMORY.name)

def status():
    if not MEMORY.exists():
        print("Visual memory: EMPTY")
        return

    records = [
        json.loads(line)
        for line in MEMORY.read_text().splitlines()
        if line.strip()
    ]

    print("S-Eye Visual Memory")
    print("Observations:", len(records))
    print(
        "Total detected objects:",
        sum(r["object_count"] for r in records)
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["save", "status"]
    )

    args = parser.parse_args()

    if args.command == "save":
        save()
    else:
        status()

if __name__ == "__main__":
    main()
