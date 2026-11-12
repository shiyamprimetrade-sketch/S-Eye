#!/usr/bin/env python3
"""S-Eye Stage 76: verified automatic memory indexing."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "visual_memory_index.json"

def execute(script, *arguments):
    result = subprocess.run(
        [sys.executable, str(ROOT / script), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    print(result.stdout, end="")

    if result.returncode:
        print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(
            f"{script} failed with code {result.returncode}"
        )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    args = parser.parse_args()

    # Preserve the previously verified index.
    previous = INDEX.read_bytes() if INDEX.exists() else None

    print("S-Eye Stage 76: Automatic memory workflow")

    try:
        execute(
            "isolated_analysis.py",
            "--image",
            str(Path(args.image).expanduser().resolve())
        )

        # Verify the currently committed index first.
        if INDEX.exists():
            execute("verify_memory_index.py")

        # Build a candidate index in the normal location.
        # The previous bytes are preserved for rollback.
        execute("build_memory_index.py")

        # Verify the rebuilt index before accepting it.
        execute("verify_memory_index.py")

    except Exception:
        if previous is None:
            INDEX.unlink(missing_ok=True)
        else:
            INDEX.write_bytes(previous)

        print(
            "S-Eye: Index restored after failure",
            file=sys.stderr
        )
        raise

    print()
    print("S-Eye Stage 76: AUTOMATIC MEMORY VERIFIED")

if __name__ == "__main__":
    main()
