#!/usr/bin/env python3
"""S-Eye unified command interface, Stage 53."""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PIPELINE = [
    ("Local contrast", "local_contrast.py"),
    ("Shape grouping", "group_shapes.py"),
    ("Region filtering", "filter_regions.py"),
    ("Camera geometry", "classify_camera_v2.py"),
]

def analyze():
    print("S-Eye Unified Vision Engine")
    print("Stage 53 — Camera analysis")
    print()

    results = []
    successful = True

    for name, filename in PIPELINE:
        script = ROOT / filename

        if not script.is_file():
            print(f"ERROR: Missing {filename}")
            successful = False
            break

        print(f"[RUNNING] {name}", flush=True)

        process = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True
        )

        if process.stdout:
            print(process.stdout.rstrip())

        if process.stderr:
            print(process.stderr.rstrip())

        passed = process.returncode == 0

        results.append({
            "step": name,
            "script": filename,
            "success": passed,
            "return_code": process.returncode,
            "output": process.stdout.strip(),
            "errors": process.stderr.strip(),
        })

        if not passed:
            print(f"[FAILED] {name}")
            successful = False
            break

        print(f"[PASS] {name}")
        print()

    report = {
        "project": "S-Eye",
        "stage": 53,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "success": successful,
        "steps": results,
    }

    output = ROOT / "s_eye_analysis.json"

    output.write_text(
        json.dumps(report, indent=2)
    )

    print("Report:", output)

    if successful:
        print("S-Eye analysis: PIPELINE PASS")
    else:
        print("S-Eye analysis: PIPELINE FAILED")
        sys.exit(1)

def status():
    print("S-Eye Unified Vision Engine")
    print("Stage 53")
    print()

    for name, filename in PIPELINE:
        exists = (ROOT / filename).is_file()
        state = "READY" if exists else "MISSING"
        print(f"{name}: {state}")

    checkpoint = ROOT / "checkpoints/stage52.json"
    print(
        "Stage 52 checkpoint:",
        "FOUND" if checkpoint.is_file() else "MISSING"
    )

def main():
    parser = argparse.ArgumentParser(
        description="S-Eye unified vision engine"
    )

    parser.add_argument(
        "command",
        choices=["analyze", "status"]
    )

    parser.add_argument(
        "--remember",
        action="store_true",
        help="Save structured visual observations"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        analyze()
        if args.remember:
            from integrate_memory import remember
            remember()
    elif args.command == "status":
        status()

if __name__ == "__main__":
    main()
