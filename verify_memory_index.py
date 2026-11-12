#!/usr/bin/env python3
"""S-Eye Stage 75: versioned memory integrity verification."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "visual_memory_index.json"
RUNS = ROOT / "isolated_runs"

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

PATTERN = re.compile(
    r"^Region\s+(\d+):\s+(.+?),\s*"
    r"corners=(\d+),\s*hull_vertices=(\d+)\s*$",
    re.MULTILINE
)

def fail(message):
    raise SystemExit("FAIL: " + message)

def digest(path):
    h = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(
            lambda: stream.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()

def parse_objects(output):
    return [
        {
            "region": int(region),
            "label": label.strip(),
            "corners": int(corners),
            "hull_vertices": int(vertices),
        }
        for region, label, corners, vertices
        in PATTERN.findall(output)
    ]

def main():
    index = json.loads(INDEX.read_text())

    if index.get("schema_version") != 1:
        fail("Unsupported index schema")

    photographs = index.get("photographs", {})

    if index.get("photograph_count") != len(photographs):
        fail("Photograph count mismatch")

    seen_runs = set()
    checked_files = 0
    checked_runs = 0

    for photo_hash, photo_entry in photographs.items():
        if photo_entry.get("photo_sha256") != photo_hash:
            fail("Photograph identity mismatch")

        for analysis in photo_entry.get("analyses", []):
            run_id = analysis["run_id"]

            if run_id in seen_runs:
                fail("Duplicate run ID: " + run_id)

            seen_runs.add(run_id)

            # Derive the trusted workspace from the run ID.
            # Do not trust arbitrary paths stored in the index.
            workspace = RUNS / run_id

            if not workspace.is_dir():
                fail("Missing workspace: " + run_id)

            if workspace.resolve().parent != RUNS.resolve():
                fail("Workspace escapes isolated_runs")

            report_path = workspace / "run_report.json"

            if not report_path.is_file():
                fail("Missing report: " + run_id)

            report = json.loads(report_path.read_text())

            if (
                report.get("run_id") != run_id
                or report.get("success") is not True
                or report.get("source_sha256") != photo_hash
            ):
                fail("Report identity mismatch: " + run_id)

            if analysis.get("created_utc") != report.get(
                "created_utc"
            ):
                fail("Run timestamp mismatch: " + run_id)

            expected_names = set(
                [report["source_photo"]] + SCRIPTS + OUTPUTS
            )

            recorded = report.get("files", {})

            if set(recorded) != expected_names:
                fail("File inventory mismatch: " + run_id)

            for name, metadata in recorded.items():
                path = workspace / name

                if not path.is_file():
                    fail("Missing file: " + name)

                if digest(path) != metadata["sha256"]:
                    fail("File hash mismatch: " + name)

                if path.stat().st_size != metadata["bytes"]:
                    fail("File size mismatch: " + name)

                checked_files += 1

            if digest(
                workspace / report["source_photo"]
            ) != photo_hash:
                fail("Source photograph changed: " + run_id)

            steps = report.get("steps", [])

            if len(steps) != len(SCRIPTS):
                fail("Pipeline length mismatch: " + run_id)

            for step, script in zip(steps, SCRIPTS):
                if (
                    step.get("script") != script
                    or step.get("success") is not True
                    or step.get("returncode") != 0
                ):
                    fail("Pipeline step invalid: " + script)

            if (
                "Source SHA-256: " + photo_hash
                not in steps[0].get("stdout", "")
            ):
                fail("Segmentation source mismatch: " + run_id)

            objects = parse_objects(steps[-1]["stdout"])

            if not objects:
                fail("No recorded classifications: " + run_id)

            if objects != analysis.get("objects"):
                fail("Indexed classification mismatch: " + run_id)

            if len(objects) != analysis.get("object_count"):
                fail("Object count mismatch: " + run_id)

            checked_runs += 1
            print("PASS:", run_id)

    if checked_runs != index.get("analysis_count"):
        fail("Analysis count mismatch")

    print()
    print("S-Eye Stage 75: MEMORY INDEX VERIFIED")
    print("Unique photographs:", len(photographs))
    print("Verified analyses:", checked_runs)
    print("Verified file fingerprints:", checked_files)
    print("Existing memory unchanged")

if __name__ == "__main__":
    main()
