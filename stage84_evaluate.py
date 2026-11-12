import json
from pathlib import Path

ROOT = Path.home() / "S/eye"
DATASET = ROOT / "stage82_dataset"

labels = json.loads(
    (DATASET / "ground_truth_draft.json").read_text()
)

index = json.loads(
    (ROOT / "visual_memory_index.json").read_text()
)

target = "20261112_200137.jpg"

reference = next(
    item for item in labels["images"]
    if item["filename"] == target
)

expected = reference["annotation"]["objects"]

photo_hash = reference["sha256"]

if photo_hash not in index["photographs"]:
    raise SystemExit("FAIL: Photograph not indexed")

analyses = index["photographs"][photo_hash]["analyses"]

def normalize(label):
    label = label.lower()

    if "circle" in label:
        return "circle"

    if "quadrilateral" in label:
        return "quadrilateral"

    if "triangle" in label:
        return "triangle"

    return "unknown"

print("S-Eye Stage 84: RECOGNITION BASELINE")
print("Reference labels:", expected)
print("Human confirmed:", reference["human_confirmed"])
print()

results = []

for analysis in analyses:
    predicted = [
        normalize(obj["label"])
        for obj in analysis["objects"]
    ]

    # Set comparison: this does not evaluate
    # object localization or repeated instances.
    matched = len(set(expected) & set(predicted))

    precision = (
        matched / len(predicted)
        if predicted else 0
    )

    recall = (
        matched / len(expected)
        if expected else 0
    )

    results.append({
        "run_id": analysis["run_id"],
        "predicted": predicted,
        "matched_classes": matched,
        "precision_proxy": precision,
        "recall_proxy": recall
    })

    print("Run:", analysis["run_id"])
    print("Predicted:", predicted)
    print("Matched classes:", matched, "/", len(expected))
    print()

output = DATASET / "stage84_baseline.json"

output.write_text(
    json.dumps({
        "stage": 84,
        "evaluation_type": "draft_class_presence",
        "ground_truth_confirmed": False,
        "localization_evaluated": False,
        "results": results
    }, indent=2)
)

print("Evaluated runs:", len(results))
print("Baseline saved:", output)
print("Status: PROVISIONAL — labels not confirmed")
