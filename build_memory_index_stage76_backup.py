#!/usr/bin/env python3
"""S-Eye Stage 74: versioned visual-memory index."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "isolated_runs"
DESTINATION = ROOT / "visual_memory_index.json"

PATTERN = re.compile(
    r"^Region\s+(\d+):\s+(.+?),\s*"
    r"corners=(\d+),\s*hull_vertices=(\d+)\s*$",
    re.MULTILINE
)

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(
            lambda: stream.read(1024 * 1024),
            b""
        ):
            h.update(chunk)
    return h.hexdigest()

def main():
    photos = {}
    run_count = 0

    for workspace in sorted(RUNS.iterdir()):
        if not workspace.is_dir():
            continue

        report_path = workspace / "run_report.json"

        if not report_path.is_file():
            continue

        report = json.loads(report_path.read_text())

        if not report.get("success"):
            continue

        photo_name = report["source_photo"]
        photo_hash = report["source_sha256"]
        photo_path = workspace / photo_name

        if (
            not photo_path.is_file()
            or digest(photo_path) != photo_hash
        ):
            raise SystemExit(
                f"FAIL: Photograph mismatch in {workspace.name}"
            )

        steps = report.get("steps", [])

        if len(steps) != 4:
            raise SystemExit(
                f"FAIL: Incomplete run {workspace.name}"
            )

        classification = steps[-1]["stdout"]

        objects = [
            {
                "region": int(region),
                "label": label.strip(),
                "corners": int(corners),
                "hull_vertices": int(vertices),
            }
            for region, label, corners, vertices
            in PATTERN.findall(classification)
        ]

        entry = photos.setdefault(
            photo_hash,
            {
                "photo_sha256": photo_hash,
                "filenames": [],
                "analyses": [],
            }
        )

        if photo_name not in entry["filenames"]:
            entry["filenames"].append(photo_name)

        entry["analyses"].append({
            "run_id": report["run_id"],
            "created_utc": report["created_utc"],
            "objects": objects,
            "object_count": len(objects),
            "workspace": str(workspace),
        })

        run_count += 1

    index = {
        "schema_version": 1,
        "project": "S-Eye",
        "stage": 74,
        "photograph_count": len(photos),
        "analysis_count": run_count,
        "photographs": photos,
    }

    DESTINATION.write_text(
        json.dumps(index, indent=2)
    )

    print("S-Eye Stage 74: INDEX CREATED")
    print("Unique photographs:", len(photos))
    print("Analysis runs:", run_count)
    print("Index:", DESTINATION)

    for photo_hash, entry in photos.items():
        print()
        print("Photo SHA-256:", photo_hash)
        print("Analyses:", len(entry["analyses"]))

        for analysis in entry["analyses"]:
            print(
                " ",
                analysis["run_id"],
                "objects:",
                analysis["object_count"]
            )

if __name__ == "__main__":
    main()
