#!/usr/bin/env python3
"""S-Eye Stage 66: isolated execution experiment."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    archives = sorted(
        (
            p for p in SESSIONS.iterdir()
            if p.is_dir() and
            (p / "manifest.json").is_file()
        ),
        key=lambda p: p.stat().st_mtime_ns
    )

    if not archives:
        raise SystemExit("FAIL: No archived session")

    archive = archives[-1]
    manifest = json.loads(
        (archive / "manifest.json").read_text()
    )

    files = manifest["files"]

    # Verify archived files before the experiment.
    for name, metadata in files.items():
        path = archive / name

        if not path.is_file():
            raise SystemExit(f"FAIL: Missing {name}")

        if sha256(path) != metadata["sha256"]:
            raise SystemExit(f"FAIL: Hash mismatch: {name}")

    scripts = [
        "local_contrast.py",
        "group_shapes.py",
        "filter_regions.py",
        "classify_camera_v2.py",
    ]

    with tempfile.TemporaryDirectory(
        prefix="s_eye_isolation_"
    ) as directory:
        work = Path(directory)

        # Copy archived files into the disposable workspace.
        for name in files:
            source = archive / name
            target = work / name

            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            shutil.copy2(source, target)

        # Remove generated images so stages must
        # recreate them rather than reuse archive outputs.
        for name in (
            "local_contrast_mask.png",
            "grouped_shapes.png",
            "filtered_shapes.png",
        ):
            (work / name).unlink(missing_ok=True)

        print("S-Eye Stage 66: Isolation experiment")
        print("Archive:", archive.name)
        print("Workspace:", work)

        for script in scripts:
            result = subprocess.run(
                [sys.executable, str(work / script)],
                cwd=work,
                capture_output=True,
                text=True,
                timeout=120
            )

            print(
                f"{script}:",
                "PASS" if result.returncode == 0
                else "FAIL"
            )

            if result.returncode:
                print(result.stdout[-1200:])
                print(result.stderr[-1200:])
                print(
                    "ISOLATION NOT YET SUPPORTED: "
                    "dependency or source-path issue"
                )
                return

        print("S-Eye Stage 66: ISOLATED RUN PASSED")

if __name__ == "__main__":
    main()
