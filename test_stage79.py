#!/usr/bin/env python3
"""S-Eye Stage 79: concurrent memory workflow test."""

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "visual_memory_index.json"
RUNS = ROOT / "isolated_runs"

PHOTO = (
    Path.home()
    / "storage/shared/DCIM/Camera/20261112_200137.jpg"
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def read_index():
    return json.loads(INDEX.read_text())


def run_ids(index):
    return {
        analysis["run_id"]
        for photo in index["photographs"].values()
        for analysis in photo["analyses"]
    }


def main():
    if not PHOTO.is_file():
        fail("Test photograph missing")

    before = read_index()
    old_ids = run_ids(before)

    print("S-Eye Stage 79: CONCURRENCY TEST")
    print("Initial runs:", len(old_ids))
    print("Launching two simultaneous workflows", flush=True)

    command = [
        sys.executable,
        str(ROOT / "auto_memory.py"),
        "--image",
        str(PHOTO),
    ]

    processes = [
        subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(2)
    ]

    results = []

    for number, process in enumerate(processes, 1):
        try:
            stdout, stderr = process.communicate(
                timeout=180
            )
        except subprocess.TimeoutExpired:
            for child in processes:
                if child.poll() is None:
                    child.kill()
            for child in processes:
                child.communicate()
            fail("Workflow timed out")

        print()
        print(f"WORKFLOW {number}")
        print(stdout[-2000:])

        if stderr:
            print(stderr[-1000:])

        results.append(process.returncode)

    if results != [0, 0]:
        fail("One or more workflows failed")

    after = read_index()
    new_ids = run_ids(after)

    added = new_ids - old_ids

    if not old_ids.issubset(new_ids):
        fail("Historical runs were lost")

    if len(added) != 2:
        fail(
            "Expected 2 new runs; found "
            + str(len(added))
        )

    verification = subprocess.run(
        [
            sys.executable,
            str(ROOT / "verify_memory_index.py"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    print(verification.stdout)

    if verification.returncode:
        print(verification.stderr)
        fail("Final memory verification failed")

    print("S-Eye Stage 79: CONCURRENCY TEST PASS")
    print("Previous runs:", len(old_ids))
    print("New runs:", len(added))
    print("Total runs:", len(new_ids))
    print("Historical runs preserved")


if __name__ == "__main__":
    main()
