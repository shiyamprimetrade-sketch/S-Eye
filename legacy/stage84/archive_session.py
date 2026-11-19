#!/usr/bin/env python3
"""S-Eye Stage 65: verified session archive."""

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifests = sorted(
        SESSIONS.glob("*.json"),
        key=lambda p: p.stat().st_mtime_ns
    )

    if not manifests:
        raise SystemExit("FAIL: No session manifest")

    manifest_path = manifests[-1]
    manifest = json.loads(manifest_path.read_text())

    session_id = manifest["session_id"]
    destination = SESSIONS / session_id

    if destination.exists():
        raise SystemExit(
            "Archive already exists. "
            "Existing files were not modified."
        )

    files = manifest["files"]
    verified = []

    # Validate every source before copying anything.
    for name, metadata in files.items():
        if name.startswith("photo/"):
            filename = name.split("/", 1)[1]
            from upgrade_memory_v2 import find_photo
            source = find_photo(filename)
        else:
            source = ROOT / name

        if not source.is_file():
            raise SystemExit(f"FAIL: Missing {name}")

        if digest(source) != metadata["sha256"]:
            raise SystemExit(
                f"FAIL: Source changed: {name}"
            )

        verified.append((name, source, metadata))

    temporary = SESSIONS / (session_id + ".tmp")

    if temporary.exists():
        raise SystemExit(
            "Temporary archive already exists. "
            "Manual inspection required."
        )

    try:
        temporary.mkdir()

        for name, source, metadata in verified:
            target = temporary / name
            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(source, target)

            if (
                digest(target) != metadata["sha256"]
                or target.stat().st_size != metadata["bytes"]
            ):
                raise ValueError(
                    f"Copy verification failed: {name}"
                )

        shutil.copy2(
            manifest_path,
            temporary / "manifest.json"
        )

        temporary.rename(destination)

    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    print("S-Eye Stage 65: ARCHIVE VERIFIED")
    print("Session:", session_id)
    print("Files copied:", len(verified))
    print("Archive:", destination)
    print("Original project files preserved")

if __name__ == "__main__":
    main()
