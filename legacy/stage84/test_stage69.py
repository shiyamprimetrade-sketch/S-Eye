#!/usr/bin/env python3
"""Stage 69: explicit-input isolated execution."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    archives = [
        p for p in SESSIONS.iterdir()
        if p.is_dir() and (p / "manifest.json").is_file()
    ]

    if not archives:
        raise SystemExit("FAIL: No archived session")

    archive = sorted(
        archives,
        key=lambda p: p.stat().st_mtime_ns
    )[-1]

    manifest = json.loads(
        (archive / "manifest.json").read_text()
    )

    photo_name = manifest["source_photo"]
    archived_photo = archive / "photo" / photo_name

    if not archived_photo.is_file():
        raise SystemExit("FAIL: Archived photo missing")

    expected_hash = manifest["files"][
        f"photo/{photo_name}"
    ]["sha256"]

    if digest(archived_photo) != expected_hash:
        raise SystemExit("FAIL: Archived photo hash mismatch")

    scripts = [
        "local_contrast.py",
        "group_shapes.py",
        "filter_regions.py",
        "classify_camera_v2.py",
    ]

    with tempfile.TemporaryDirectory(
        prefix="s_eye_stage69_"
    ) as directory:
        work = Path(directory)

        shutil.copy2(
            archived_photo,
            work / photo_name
        )

        # Use the updated segmentation script.
        shutil.copy2(
            ROOT / "local_contrast.py",
            work / "local_contrast.py"
        )

        for script in scripts[1:]:
            shutil.copy2(
                archive / script,
                work / script
            )

        print("S-Eye Stage 69: Isolated input test")
        print("Photo:", photo_name)
        print("Photo hash:", expected_hash)

        for script in scripts:
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

            print(
                script,
                "PASS" if result.returncode == 0
                else "FAIL"
            )

            if result.returncode:
                print(result.stdout[-1500:])
                print(result.stderr[-1500:])
                raise SystemExit(
                    "FAIL: Isolated pipeline incomplete"
                )

            if script == "local_contrast.py":
                expected_line = (
                    "Source SHA-256: " + expected_hash
                )

                if expected_line not in result.stdout:
                    raise SystemExit(
                        "FAIL: Segmentation source mismatch"
                    )

        reference_mask = (
            archive / "local_contrast_mask.png"
        )

        generated_mask = (
            work / "local_contrast_mask.png"
        )

        if not generated_mask.is_file():
            raise SystemExit(
                "FAIL: Segmentation mask missing"
            )

        same_mask = (
            digest(reference_mask)
            == digest(generated_mask)
        )

        print(
            "Segmentation matches archived reference:",
            same_mask
        )

        if not same_mask:
            raise SystemExit(
                "FAIL: Segmentation output differs"
            )

        print("S-Eye Stage 69: ISOLATED INPUT PASS")

if __name__ == "__main__":
    main()
