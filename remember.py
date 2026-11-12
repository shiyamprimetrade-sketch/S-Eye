import json
from pathlib import Path

memory_file = Path("eye_memory.jsonl")

if not memory_file.exists():
    print("S-Eye: No memories found")
    exit()

with memory_file.open() as f:
    memories = [json.loads(line) for line in f if line.strip()]

print("S-Eye: I remember", len(memories), "observations")

if memories:
    last = memories[-1]

    print("Last photograph:", last["photo"])
    print("Brightness:", last["brightness"])
    print("Vision:", last["vision"])
    print("Dominant color:", last["dominant_color"])
    print("Detected edges:", last["edge_count"])
    print("Visual regions:", last["regions"])
