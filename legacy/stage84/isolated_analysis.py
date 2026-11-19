#!/usr/bin/env python3
"""S-Eye Stage 71: persistent isolated image analysis."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
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

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, required=True)
    args = parser.parse_args()

    photo = args.image.expanduser().resolve()

    if not photo.is_file():
        parser.error("Specified photograph does not exist")

    if photo.suffix.lower() not in (".jpg", ".jpeg", ".png"):
        parser.error("Unsupported photograph format")

    RUNS.mkdir(exist_ok=True)

    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "-"
        + uuid.uuid4().hex[:12]
    )

    workspace = RUNS / run_id
    workspace.mkdir()

    photo_copy = workspace / photo.name
    shutil.copy2(photo, photo_copy)

    initial_hash = digest(photo_copy)

    for script in SCRIPTS:
        shutil.copy2(ROOT / script, workspace / script)

    steps = []
    success = True

    for script in SCRIPTS:
        command = [sys.executable, script]

        if script == "local_contrast.py":
            command += ["--image", str(photo_copy)]

        result = subprocess.run(
            command,
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=120,
        )

        passed = result.returncode == 0

        if script == "local_contrast.py":
            passed = passed and (
                "Source SHA-256: " + initial_hash
                in result.stdout
            )

        steps.append({
            "script": script,
            "success": passed,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })

        print(
            f"{script}:",
            "PASS" if passed else "FAIL"
        )

        if not passed:
            success = False
            break

    if digest(photo_copy) != initial_hash:
        success = False
        print("FAIL: Workspace photograph changed")

    if success:
        for name in OUTPUTS:
            if not (workspace / name).is_file():
                success = False
                print("FAIL: Missing", name)

    files = {}

    for path in sorted(workspace.iterdir()):
        if path.is_file():
            files[path.name] = {
                "sha256": digest(path),
                "bytes": path.stat().st_size,
            }

    report = {
        "schema_version": 1,
        "stage": 71,
        "run_id": run_id,
        "source_photo": photo.name,
        "source_sha256": initial_hash,
        "success": success,
        "steps": steps,
        "files": files,
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    report_path = workspace / "run_report.json"

    report_path.write_text(
        json.dumps(report, indent=2)
    )

    print("Run ID:", run_id)
    print("Workspace:", workspace)
    print("Files recorded:", len(files))
    print(
        "S-Eye isolated analysis:",
        "PASS" if success else "FAIL"
    )

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
