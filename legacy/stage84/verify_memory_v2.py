#!/usr/bin/env python3
"""S-Eye Stage 59: visual memory v2 verification."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEMORY = ROOT / "visual_memory_v2.jsonl"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(records, photo_resolver):
    errors = []
    observation_ids = set()
    object_ids = set()

    for index, record in enumerate(records, 1):
        prefix = f"Observation {index}"

        if not isinstance(record, dict):
            errors.append(f"{prefix}: invalid record")
            continue

        if record.get("schema_version") != 2:
            errors.append(f"{prefix}: invalid schema")
            continue

        oid = record.get("observation_id")

        if not isinstance(oid, str) or not oid:
            errors.append(f"{prefix}: invalid observation ID")
            continue

        if oid in observation_ids:
            errors.append(f"{prefix}: duplicate observation ID")

        observation_ids.add(oid)

        photo_hash = record.get("photo_sha256")

        if not isinstance(photo_hash, str):
            errors.append(f"{prefix}: missing photo hash")
            continue

        try:
            if len(photo_hash) != 64:
                raise ValueError()
            int(photo_hash, 16)
        except ValueError:
            errors.append(f"{prefix}: invalid photo hash")
            continue

        photo = photo_resolver(record.get("photo", ""))

        if photo is None:
            errors.append(f"{prefix}: photograph missing")
        elif digest(photo) != photo_hash:
            errors.append(f"{prefix}: photograph hash mismatch")

        size = record.get("processed_image_size")

        if (
            not isinstance(size, list)
            or len(size) != 2
            or any(type(v) is not int or v <= 0 for v in size)
        ):
            errors.append(f"{prefix}: invalid image size")
            continue

        width, height = size
        objects = record.get("objects")

        if not isinstance(objects, list):
            errors.append(f"{prefix}: invalid objects")
            continue

        if record.get("object_count") != len(objects):
            errors.append(f"{prefix}: object count mismatch")

        for obj in objects:
            if not isinstance(obj, dict):
                errors.append(f"{prefix}: invalid object")
                continue

            object_id = obj.get("object_id")
            region = obj.get("region_id")

            if (
                type(region) is not int
                or region < 1
                or object_id != f"{oid}:{region}"
            ):
                errors.append(f"{prefix}: invalid object ID")
                continue

            if object_id in object_ids:
                errors.append(f"{prefix}: duplicate object ID")

            object_ids.add(object_id)

            box = obj.get("bbox")

            if (
                not isinstance(box, list)
                or len(box) != 4
                or any(type(v) is not int for v in box)
            ):
                errors.append(f"{prefix}: invalid bounding box")
                continue

            x1, y1, x2, y2 = box

            if not (
                0 <= x1 <= x2 < width
                and 0 <= y1 <= y2 < height
            ):
                errors.append(f"{prefix}: bounding box outside image")

    return errors

def resolve_photo(filename):
    if not isinstance(filename, str):
        return None

    # Accept filenames only, never arbitrary paths.
    if Path(filename).name != filename:
        return None

    candidates = [
        ROOT / filename,
        Path.home() / "storage/shared/DCIM/Camera" / filename,
    ]

    return next(
        (path for path in candidates if path.is_file()),
        None
    )

def main():
    print("S-Eye Stage 59 — Memory Verification")

    if not MEMORY.is_file():
        raise SystemExit("FAIL: Memory v2 missing")

    try:
        records = [
            json.loads(line)
            for line in MEMORY.read_text().splitlines()
            if line.strip()
        ]
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise SystemExit(f"FAIL: Corrupted JSONL: {exc}")

    if not records:
        raise SystemExit("FAIL: Memory is empty")

    errors = verify(records, resolve_photo)

    if errors:
        for error in errors:
            print("FAIL:", error)
        sys.exit(1)

    print("PASS: Memory schema valid")
    print("PASS: Photograph hashes match")
    print("PASS: Observation IDs unique")
    print("PASS: Object IDs valid")
    print("PASS: Bounding boxes valid")
    print("Observations:", len(records))
    print(
        "Objects:",
        sum(len(r["objects"]) for r in records)
    )
    print("S-Eye Stage 59: VERIFICATION PASSED")

if __name__ == "__main__":
    main()
