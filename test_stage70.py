#!/usr/bin/env python3
"""S-Eye Stage 70: isolated classification reproducibility."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"

SCRIPTS = [
    "local_contrast.py",
    "group_shapes.py",
    "filter_regions.py",
    "classify_camera_v2.py",
]

PATTERN = re.compile(
    r"^Region\s+(\d+):\s+(.+?),\s*"
    r"corners=(\d+),\s*hull_vertices=(\d+)\s*$",
    re.MULTILINE
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def classifications(output):
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
    archives = sorted(
        (
            p for p in SESSIONS.iterdir()
            if p.is_dir()
            and (p / "manifest.json").is_file()
        ),
        key=lambda p: p.stat().st_mtime_ns
    )

    if not archives:
        raise SystemExit("FAIL: No session archive")

    archive = archives[-1]

    manifest = json.loads(
        (archive / "manifest.json").read_text()
    )

    # Verify archived evidence before using it.
    for name, metadata in manifest["files"].items():
        path = archive / name

        if (
            not path.is_file()
            or digest(path) != metadata["sha256"]
        ):
            raise SystemExit(
                f"FAIL: Archived file mismatch: {name}"
            )

    report = json.loads(
        (archive / "s_eye_analysis.json").read_text()
    )

    reference_step = next(
        step for step in report["steps"]
        if step["script"] == "classify_camera_v2.py"
    )

    expected = classifications(reference_step["output"])

    if not expected:
        raise SystemExit(
            "FAIL: No archived classifications found"
        )

    photo_name = manifest["source_photo"]
    photo = archive / "photo" / photo_name

    with tempfile.TemporaryDirectory(
        prefix="s_eye_stage70_"
    ) as directory:
        work = Path(directory)

        shutil.copy2(photo, work / photo_name)

        shutil.copy2(
            ROOT / "local_contrast.py",
            work / "local_contrast.py"
        )

        for script in SCRIPTS[1:]:
            shutil.copy2(
                archive / script,
                work / script
            )

        observed = None

        for script in SCRIPTS:
            command = [
                sys.executable,
                str(work / script)
            ]

            if script == "local_contrast.py":
                command += [
                    "--image",
                    str(work / photo_name)
                ]

            result = subprocess.run(
                command,
                cwd=work,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(result.stdout[-1000:])
                print(result.stderr[-1000:])
                raise SystemExit(
                    f"FAIL: {script}"
                )

            print(f"{script}: PASS")

            if script == "local_contrast.py":
                expected_hash = manifest["files"][
                    f"photo/{photo_name}"
                ]["sha256"]

                if (
                    "Source SHA-256: " + expected_hash
                ) not in result.stdout:
                    raise SystemExit(
                        "FAIL: Incorrect source photograph"
                    )

            if script == "classify_camera_v2.py":
                observed = classifications(result.stdout)

        print()
        print("Archived classifications:")
        for item in expected:
            print(item)

        print()
        print("Isolated classifications:")
        for item in observed:
            print(item)

        if observed != expected:
            raise SystemExit(
                "FAIL: Classification mismatch"
            )

        print()
        print("S-Eye Stage 70: CLASSIFICATIONS REPRODUCED")
        print("Matching regions:", len(expected))

if __name__ == "__main__":
    main()
