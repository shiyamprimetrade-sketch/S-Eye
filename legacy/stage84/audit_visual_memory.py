#!/usr/bin/env python3
"""S-Eye Stage 57: read-only visual memory audit."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEMORY = ROOT / "visual_memory.jsonl"
REPORT = ROOT / "s_eye_analysis.json"

def fail(message):
    print("FAIL:", message)
    sys.exit(1)

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def main():
    print("S-Eye Stage 57 — Visual Memory Audit")

    if not MEMORY.is_file():
        fail("Visual memory missing")

    records = []

    for number, line in enumerate(
        MEMORY.read_text().splitlines(), 1
    ):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            fail(f"Invalid JSON at line {number}")

        if not isinstance(record, dict):
            fail(f"Invalid record at line {number}")

        records.append(record)

    if not records:
        fail("No observations")

    seen_reports = set()
    seen_objects = set()

    for index, record in enumerate(records, 1):
        if record.get("schema_version") != 1:
            fail(f"Unsupported schema in record {index}")

        report_hash = record.get("report_sha256")

        if not isinstance(report_hash, str):
            fail(f"Missing report hash in record {index}")

        if len(report_hash) != 64:
            fail(f"Invalid report hash in record {index}")

        try:
            int(report_hash, 16)
        except ValueError:
            fail(f"Non-hexadecimal hash in record {index}")

        if report_hash in seen_reports:
            fail(f"Duplicate report in record {index}")

        seen_reports.add(report_hash)

        objects = record.get("objects")

        if not isinstance(objects, list):
            fail(f"Invalid objects in record {index}")

        if record.get("object_count") != len(objects):
            fail(f"Object count mismatch in record {index}")

        observation_id = report_hash[:16]

        for obj in objects:
            if not isinstance(obj, dict):
                fail("Invalid object")

            region = obj.get("region_id")

            if not isinstance(region, int) or region < 1:
                fail("Invalid region identifier")

            object_id = f"{observation_id}:{region}"

            if object_id in seen_objects:
                fail(f"Duplicate object ID: {object_id}")

            seen_objects.add(object_id)

            box = obj.get("bbox")

            if (
                not isinstance(box, list)
                or len(box) != 4
                or any(type(v) is not int for v in box)
                or box[0] > box[2]
                or box[1] > box[3]
            ):
                fail(f"Invalid bounding box: {object_id}")

        print(
            f"PASS: Observation {index}, "
            f"objects={len(objects)}, "
            f"id={observation_id}"
        )

    current_hash = sha256(REPORT.read_bytes()) if REPORT.exists() else None

    matches = sum(
        record["report_sha256"] == current_hash
        for record in records
    )

    print("PASS: Memory structure valid")
    print("PASS: No duplicate report hashes")
    print("PASS: Object identifiers unique")
    print("Current report hash matches:", matches)
    print("Observations audited:", len(records))
    print("Objects audited:", len(seen_objects))

    if matches == 0:
        print(
            "NOTE: No record matches the current report. "
            "Historical reports cannot be verified here."
        )

    print("S-Eye Stage 57: AUDIT PASSED")

if __name__ == "__main__":
    main()
