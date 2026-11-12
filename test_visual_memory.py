import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEMORY = ROOT / "visual_memory.jsonl"

def load():
    return [
        json.loads(line)
        for line in MEMORY.read_text().splitlines()
        if line.strip()
    ]

def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print("PASS:", message)

print("S-Eye Stage 56 — Memory Integrity Tests")

before = load()

check(
    len(before) >= 1,
    "Visual memory contains observations"
)

record = before[-1]

check(
    record["schema_version"] == 1,
    "Schema version valid"
)

check(
    record["object_count"] == len(record["objects"]),
    "Object count consistent"
)

check(
    len(record["report_sha256"]) == 64,
    "Report hash format valid"
)

ids = [obj["region_id"] for obj in record["objects"]]

check(
    len(ids) == len(set(ids)),
    "Region identifiers unique"
)

for obj in record["objects"]:
    box = obj["bbox"]

    check(
        len(box) == 4
        and box[0] <= box[2]
        and box[1] <= box[3],
        f"Region {obj['region_id']} bounding box valid"
    )

result = subprocess.run(
    [sys.executable, "visual_memory.py", "save"],
    cwd=ROOT,
    capture_output=True,
    text=True
)

check(
    result.returncode == 0,
    "Repeated save command succeeds"
)

after = load()

check(
    len(after) == len(before),
    "Duplicate observation prevented"
)

check(
    before == after,
    "Existing observations unchanged"
)

check(
    "already recorded" in result.stdout,
    "Duplicate detection reported"
)

print()
print("S-Eye Stage 56: ALL TESTS PASSED")
print("Observations:", len(after))
print(
    "Objects in latest observation:",
    after[-1]["object_count"]
)
