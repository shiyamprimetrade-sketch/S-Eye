from pathlib import Path

target = Path("auto_memory.py")
backup = Path("auto_memory_stage77_backup.py")

source = target.read_text()

if not backup.exists():
    backup.write_text(source)

if "STAGE78_WORKFLOW_LOCK" in source:
    print("Stage 78 already installed")
    raise SystemExit(0)

replacement = '''#!/usr/bin/env python3
"""S-Eye Stage 78: locked automatic memory workflow."""

# STAGE78_WORKFLOW_LOCK

import argparse
import fcntl
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "visual_memory_index.json"
LOCK = ROOT / ".visual_memory_workflow.lock"


def execute(script, *arguments):
    result = subprocess.run(
        [sys.executable, str(ROOT / script), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    print(result.stdout, end="", flush=True)

    if result.returncode:
        print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(
            f"{script} failed: {result.returncode}"
        )


def atomic_restore(previous):
    if previous is None:
        INDEX.unlink(missing_ok=True)
        return

    temp_name = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=ROOT,
            prefix=".visual_memory_restore.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temp_name = stream.name
            stream.write(previous)
            stream.flush()
            os.fsync(stream.fileno())

        os.replace(temp_name, INDEX)
        temp_name = None

        directory_fd = os.open(ROOT, os.O_RDONLY)

        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--image",
        required=True,
        help="Photograph to analyze"
    )

    args = parser.parse_args()

    image = Path(args.image).expanduser().resolve()

    if not image.is_file():
        parser.error("Photograph does not exist")

    with LOCK.open("a+b") as lock:
        print(
            "S-Eye Stage 78: Waiting for workflow lock",
            flush=True
        )

        fcntl.flock(lock, fcntl.LOCK_EX)

        try:
            print(
                "S-Eye Stage 78: Workflow lock acquired",
                flush=True
            )

            # Validate the existing index before modification.
            if INDEX.exists():
                execute("verify_memory_index.py")

            previous = (
                INDEX.read_bytes()
                if INDEX.exists()
                else None
            )

            try:
                execute(
                    "isolated_analysis.py",
                    "--image",
                    str(image)
                )

                execute("build_memory_index.py")

                execute("verify_memory_index.py")

            except Exception:
                atomic_restore(previous)

                print(
                    "S-Eye: Previous index restored",
                    file=sys.stderr
                )

                raise

            print()
            print(
                "S-Eye Stage 78: LOCKED MEMORY VERIFIED"
            )

        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


if __name__ == "__main__":
    main()
'''

compile(replacement, str(target), "exec")

target.write_text(replacement)

print("S-Eye Stage 78: Installed")
print("Backup:", backup)
