#!/usr/bin/env python3
"""S-Eye Stage 80: failure recovery verification."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "visual_memory_index.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if not INDEX.is_file():
        raise SystemExit("FAIL: Memory index missing")

    before = INDEX.read_bytes()
    before_hash = digest(before)
    before_index = json.loads(before)

    print("S-Eye Stage 80: FAILURE RECOVERY TEST")
    print("Initial index SHA-256:", before_hash)

    with tempfile.TemporaryDirectory() as directory:
        invalid_photo = Path(directory) / "invalid.jpg"

        invalid_photo.write_bytes(
            b"This is not a valid JPEG photograph."
        )

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "auto_memory.py"),
                "--image",
                str(invalid_photo),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )

        print("Failure test exit code:", result.returncode)

        if result.returncode == 0:
            raise SystemExit(
                "FAIL: Invalid photograph was accepted"
            )

    after = INDEX.read_bytes()
    after_hash = digest(after)

    if before_hash != after_hash:
        raise SystemExit(
            "FAIL: Memory index changed after failure"
        )

    after_index = json.loads(after)

    if before_index != after_index:
        raise SystemExit(
            "FAIL: Historical memory changed"
        )

    verification = subprocess.run(
        [
            sys.executable,
            str(ROOT / "verify_memory_index.py"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    print(verification.stdout)

    if verification.returncode:
        print(verification.stderr)
        raise SystemExit(
            "FAIL: Memory integrity verification failed"
        )

    print("S-Eye Stage 80: FAILURE RECOVERY PASS")
    print("Index SHA-256 unchanged:", before_hash == after_hash)
    print("Historical analyses:", after_index["analysis_count"])
    print("Memory preserved")


if __name__ == "__main__":
    main()
