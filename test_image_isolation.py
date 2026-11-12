#!/usr/bin/env python3
"""S-Eye Stage 67: photograph isolation audit."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"

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

    photo = manifest["source_photo"]

    with tempfile.TemporaryDirectory(
        prefix="s_eye_source_test_"
    ) as directory:
        work = Path(directory)

        shutil.copy2(
            archive / "local_contrast.py",
            work / "local_contrast.py"
        )

        # Intentionally do NOT copy the photograph.
        # The disposable directory contains only the script.

        result = subprocess.run(
            [sys.executable, "local_contrast.py"],
            cwd=work,
            capture_output=True,
            text=True,
            timeout=120
        )

        print("S-Eye Stage 67: Source isolation audit")
        print("Expected archived photo:", photo)
        print("Workspace photograph: ABSENT")
        print("Exit code:", result.returncode)
        print("Segmentation output:")
        print(result.stdout[-1500:])
        print(result.stderr[-1000:])

        if result.returncode == 0:
            print(
                "RESULT: EXTERNAL SOURCE DEPENDENCY DETECTED"
            )
            print(
                "Segmentation succeeded without an image "
                "inside the isolated workspace."
            )
        else:
            print(
                "RESULT: NO SUCCESS WITHOUT WORKSPACE PHOTO"
            )
            print(
                "Inspect the error to determine whether "
                "the failure was caused by missing image "
                "or another dependency."
            )

if __name__ == "__main__":
    main()
