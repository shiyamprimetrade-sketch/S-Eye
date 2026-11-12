import json
from pathlib import Path

path = Path("eye_memory.jsonl")

with path.open() as f:
    memories = [json.loads(line) for line in f if line.strip()]

if len(memories) < 2:
    print("S-Eye: Need two observations to compare")
    raise SystemExit

old = memories[-2]
new = memories[-1]

print("S-Eye: Comparing experiences")
print("Previous:", old["photo"])
print("Current:", new["photo"])

if old["photo"] == new["photo"]:
    print("Warning: Both observations use the same photograph")

change = new["brightness"] - old["brightness"]

if change > 10:
    print("Observation: Brighter than before")
elif change < -10:
    print("Observation: Darker than before")
else:
    print("Observation: Similar average brightness")

print("Brightness change:", change)
print("Edge count change:", new["edge_count"] - old["edge_count"])
print("Previous active region:", max(old["regions"], key=old["regions"].get))
print("Current active region:", max(new["regions"], key=new["regions"].get))
