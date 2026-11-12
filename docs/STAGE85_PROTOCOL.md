# Stage 85 generalization protocol

Purpose: measure the existing S-Eye camera geometry pipeline on previously unseen
photographs while keeping original bytes and visual memory unchanged.

## What is implemented

`generalization.py` runs local contrast segmentation, grouping, region filtering
and camera classification in a fresh temporary directory for every case. It
requires explicit input, checks its SHA-256, validates classifier output counts,
and records stdout, class predictions and generated artifact hashes. No weights,
external models, classifier thresholds, or historical checkpoints are changed.

The eight conditions are original bytes, brightness ×0.55, brightness ×1.3,
contrast ×0.45, rotation ±15 degrees, affine shear x'=x+0.15y−0.075h (inverse
sampling coefficients), and JPEG quality 50. Rotation expands the canvas. Warps
and white borders can change segmentation: these are perturbation probes, not
physical camera captures. JPEG output is decoded and saved as PNG before analysis.

## Reproduce the public benchmark

From the repository directory, with Python 3.12 or 3.13:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python stage85_fixture.py /tmp/s-eye-stage85 --stress
python generalization.py --manifest /tmp/s-eye-stage85/manifest.json --output /tmp/s-eye-stage85-report.json
```

Choose unused paths on subsequent runs. Existing reports are never overwritten.
The default fixture (omit `--stress`) contains three outlined shapes and a blank
negative control. Stress adds a faint triangle, a tiny circle, and an elongated
quadrilateral. The last cases deliberately expose contrast, size and aspect-ratio
limits. Fixture images are generated locally and are not photographs. Compare
predictions and artifact hashes within the same Python/Pillow versions; other
versions may differ. Runtime details and source hashes are in each report.

## Evaluate independently captured photographs

Capture at least three **new** photographs of the same shapes using different
physical camera angles and illumination. For an initial capture matrix use
frontal/diffuse, oblique/diffuse and frontal/dim. Then add oblique/dim and multiple
backgrounds; record approximate angles if measured and `unknown` if not measured.
Do not use repeats of the original Stage 84 photo as new sources. Keep labels
independent of S-Eye output. Use separate development and held-out capture groups
if thresholds are later tuned; record this split before tuning.

Put the photographs and `manifest.json` in one directory. Each entry follows this
schema (replace the hash and metadata with actual values):

```json
{
  "schema_version": 1,
  "images": [
    {
      "id": "capture-01",
      "path": "photo01.jpg",
      "sha256": "REPLACE_WITH_ACTUAL_SHA256",
      "source_kind": "photograph",
      "capture_group": "heldout-session-02",
      "lighting": "diffuse_daylight",
      "camera_angle": "oblique_unmeasured",
      "annotation_source": "Shiyam visual review before evaluation",
      "human_confirmed": true,
      "expected_classes": ["circle", "quadrilateral", "triangle"]
    }
  ]
}
```

Use `sha256sum photo01.jpg` to obtain the hash. `human_confirmed` is a recorded
annotation declaration, not proof of review supplied by the software. Set it to
false for draft annotations. No example hash is presented as measured evidence.
The evaluator accepts only circle, quadrilateral and triangle; it cannot evaluate
wardrobes, hands or other object identities. Empty lists are valid negative controls.
Images must be inside the manifest directory; duplicate source bytes are rejected.

```bash
python generalization.py --manifest /path/to/photos/manifest.json --output /path/to/new-report.json
```

Reports retain lighting, angle, capture group and annotation provenance for each
case. Summary rows separate photographs from synthetic images, confirmed from
draft labels, and every perturbation condition. The source count is independent
of variant count. `confirmed_photographs` counts declarations, not camera-authenticity
verification. Inspect condition results and per-image failures; do not combine
correlated variants into an independent-sample accuracy or confidence interval.

## Metric and failure interpretation

Class-presence precision uses unique predicted classes, including unknown as a
false positive. Recall uses unique expected classes. Square-like, Rectangle-like
and Ambiguous quadrilateral all map to quadrilateral. Duplicate detections do not
change these set metrics. Undefined precision/recall is null; an empty prediction
matches an empty expected set exactly. Instance counts and bounding boxes are not
evaluated. Class presence can hide duplicate false detections.

A pipeline error remains in the summary denominator and is never an exact match.
The CLI writes its report and exits 1 for pipeline failures. Incorrect predictions
are experimental findings and exit 0 when execution succeeded; unit tests provide
regression gates separately. Invalid data exits 2 before evaluation. The report
contains logs and image-derived hashes; review before publishing private captures.

## Completion gates

- Implemented: portable evaluator, source verification, isolated execution,
  reproducible synthetic controls, regression tests, CI and evidence checkpoint.
- Pending: three or more new, human-reviewed photographs with recorded capture
  conditions; compare original-photo results per condition and preserve report.
- Pending: localization and repeated-instance annotations, realistic clutter,
  occlusion, wider devices and physically measured viewpoint sweeps.

Do not label Stage 85 photographic generalization complete until actual capture
results exist. Tune the engine only after a measured failure is reproduced on a
separate development set; evaluate the fix on held-out captures.
