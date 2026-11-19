import json
from pathlib import Path

root = Path.home() / "S/eye/stage82_dataset"
manifest = json.loads((root / "manifest.json").read_text())

labels = {
    "20261112_193052.jpg": {
        "objects": ["wardrobe", "chest_of_drawers"],
        "task": "object_recognition"
    },
    "20261112_193338.jpg": {
        "objects": ["hand", "wardrobe", "chest_of_drawers"],
        "task": "occlusion"
    },
    "20261112_194129.jpg": {
        "objects": ["extension_strip", "electrical_cable"],
        "task": "foreground_segmentation"
    },
    "20261112_194407.jpg": {
        "objects": ["wooden_surface", "fabric"],
        "task": "scene_comparison"
    },
    "20261112_194411.jpg": {
        "objects": ["wooden_surface", "fabric"],
        "task": "scene_comparison"
    },
    "20261112_194422.jpg": {
        "objects": ["wooden_surface", "fabric", "green_rectangle"],
        "task": "change_detection"
    },
    "20261112_200137.jpg": {
        "objects": ["circle", "quadrilateral", "triangle"],
        "task": "shape_recognition"
    }
}

dataset = []

for entry in manifest:
    filename = entry["filename"]

    if filename not in labels:
        raise SystemExit(f"Missing label: {filename}")

    dataset.append({
        "filename": filename,
        "sha256": entry["sha256"],
        "annotation": labels[filename],
        "annotation_source": "assistant_contact_sheet_review",
        "human_confirmed": False,
        "bounding_boxes": None
    })

output = root / "ground_truth_draft.json"

output.write_text(
    json.dumps({
        "schema_version": 1,
        "stage": 83,
        "status": "draft_unconfirmed",
        "images": dataset
    }, indent=2)
)

print("S-Eye Stage 83: LABEL DRAFT CREATED")
print("Photographs:", len(dataset))
print("Labels:", sum(
    len(item["annotation"]["objects"])
    for item in dataset
))
print("Human confirmation: PENDING")
print("Output:", output)
