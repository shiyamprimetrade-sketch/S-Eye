"""S-Eye Stage 62: source-image consistency guard."""

import hashlib
import re
from pathlib import Path

from integrate_memory import remember
from upgrade_memory_v2 import find_photo

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def identify_source():
    script = ROOT / "local_contrast.py"
    text = script.read_text()

    # The existing pipeline selects the newest camera JPG.
    # Identify the selected source from its latest report
    # only after analysis. For pre-analysis verification,
    # inspect the current camera directory.
    camera = Path.home() / "storage/shared/DCIM/Camera"

    photos = list(camera.glob("*.jpg")) + list(
        camera.glob("*.JPG")
    )

    if not photos:
        raise FileNotFoundError("No camera JPG found")

    return max(photos, key=lambda p: p.stat().st_mtime)

def guarded_analysis(analyze):
    source = identify_source()

    before = digest(source)

    print("S-Eye: Source guard enabled")
    print("Source:", source.name)
    print("Initial SHA-256:", before)

    analyze()

    after = digest(source)

    if before != after:
        raise RuntimeError(
            "Source photograph changed during analysis. "
            "Memory write blocked."
        )

    # Verify that segmentation reports this photograph.
    from json import loads

    report = loads(
        (ROOT / "s_eye_analysis.json").read_text()
    )

    output = next(
        step["output"]
        for step in report["steps"]
        if step["script"] == "local_contrast.py"
    )

    match = re.search(
        r"^Photo: (.+)$",
        output,
        re.MULTILINE
    )

    if not match or match.group(1).strip() != source.name:
        raise RuntimeError(
            "Source mismatch between guard and segmentation. "
            "Memory write blocked."
        )

    print("S-Eye: Source integrity verified")

    remember()
