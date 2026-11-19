#!/usr/bin/env python3
"""S-Eye Stage 72: independent isolated-run verifier."""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "isolated_runs"
ARCHIVES = ROOT / "sessions"

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

def digest(path):
    h = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(
            lambda: stream.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()

def labels(output):
    return [
        (
            int(region),
            label.strip(),
            int(corners),
            int(vertices)
        )
        for region, label, corners, vertices
        in PATTERN.findall(output)
    ]

def fail(message):
    raise SystemExit("FAIL: " + message)

def main():
    runs = [
        p for p in RUNS.iterdir()
        if p.is_dir()
        and (p / "run_report.json").is_file()
    ]

    if not runs:
        fail("No isolated runs found")

    run = max(
        runs,
        key=lambda p: p.stat().st_mtime_ns
    )

    report = json.loads(
        (run / "run_report.json").read_text()
    )

    if not report.get("success"):
        fail("Run report indicates failure")

    if report.get("run_id") != run.name:
        fail("Run ID mismatch")

    expected_files = set(
        [report["source_photo"]]
        + SCRIPTS
        + OUTPUTS
    )

    recorded_files = report.get("files", {})

    if set(recorded_files) != expected_files:
        fail("Unexpected file inventory")

    for name, metadata in recorded_files.items():
        path = run / name

        if not path.is_file():
            fail("Missing file: " + name)

        if digest(path) != metadata["sha256"]:
            fail("SHA-256 mismatch: " + name)

        if path.stat().st_size != metadata["bytes"]:
            fail("File size mismatch: " + name)

    print("PASS: Eight file fingerprints verified")

    photo = run / report["source_photo"]

    if digest(photo) != report["source_sha256"]:
        fail("Source photograph hash mismatch")

    print("PASS: Photograph integrity verified")

    steps = report.get("steps", [])

    if len(steps) != len(SCRIPTS):
        fail("Incorrect pipeline length")

    for step, script in zip(steps, SCRIPTS):
        if (
            step.get("script") != script
            or not step.get("success")
            or step.get("returncode") != 0
        ):
            fail("Pipeline step mismatch: " + script)

    source_line = (
        "Source SHA-256: "
        + report["source_sha256"]
    )

    if source_line not in steps[0]["stdout"]:
        fail("Segmentation source hash mismatch")

    print("PASS: Four pipeline stages verified")

    observed = labels(steps[-1]["stdout"])

    if not observed:
        fail("No classifications recorded")

    archives = [
        p for p in ARCHIVES.iterdir()
        if p.is_dir()
        and (p / "manifest.json").is_file()
    ]

    reference = None

    for archive in archives:
        manifest = json.loads(
            (archive / "manifest.json").read_text()
        )

        photo_key = (
            "photo/" + report["source_photo"]
        )

        metadata = manifest.get(
            "files", {}
        ).get(photo_key)

        if not metadata:
            continue

        if (
            metadata["sha256"]
            != report["source_sha256"]
        ):
            continue

        reference = archive
        break

    if reference is None:
        fail("No matching archived reference")

    reference_report = json.loads(
        (reference / "s_eye_analysis.json").read_text()
    )

    reference_step = next(
        (
            step for step
            in reference_report["steps"]
            if step["script"]
            == "classify_camera_v2.py"
        ),
        None
    )

    if reference_step is None:
        fail("Reference classification missing")

    expected = labels(reference_step["output"])

    if not expected:
        fail("Reference contains no classifications")

    if observed != expected:
        print("Expected:", expected)
        print("Observed:", observed)
        fail("Classification mismatch")

    print(
        "PASS: Classifications reproduced:",
        len(observed)
    )

    print()
    print("S-Eye Stage 72: RUN VERIFIED")
    print("Run:", run.name)
    print("Files:", len(recorded_files))
    print("Objects:", len(observed))
    print("No files modified")

if __name__ == "__main__":
    main()
