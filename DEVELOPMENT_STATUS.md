# S-Eye development status

Pull request: https://github.com/shiyamprimetrade-sketch/S-Eye/pull/1

Checkpoint date: 2026-11-12. Branch: `development/stage85-generalization`.

## Completed milestones

- Stage 84 source baseline audited and inventoried at commit `e92bb55`.
- Stage 85 executable evaluation milestone: portable photo manifest, strict
  hashes, isolated unchanged camera pipeline, eight perturbation conditions,
  explicit class taxonomy, class-presence metrics and evidence reports.
- Automated verification: 18 tests passed on Python 3.12.14 / Pillow 13.0.0.
  Includes legacy geometry, pipeline repeatability, no repository writes,
  source corruption/duplicates, EXIF input, blank control, metric edge cases,
  controlled failure accounting and preservation of existing reports.
- Reproducible synthetic benchmark: 56 executions from 7 distinct generated
  images × 8 conditions; 56 completed, 42 exact class-set matches, 14 mismatches.
  All 32 simple-control cases matched; the faint triangle failed all eight
  conditions, and elongated quadrilateral failed six (rotation ±15 succeeded).
  These are geometric stress findings, **not photographic recognition accuracy**.
- Historical synthetic regressions reproduced: rotation stress 20/20,
  six geometry-challenge labels, uncertainty rules 9/9. Existing borderline
  geometry weakness reproduced at 4/8 and preserved explicitly.
- GitHub Actions workflow added for Python 3.12 and 3.13; uploads benchmark report.
  Remote CI passed on commit `88a7673` in both Python jobs:
  https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43250792252
  This checkpoint adds a malformed-row test correction and updated local evidence;
  inspect its own run before extending the CI claim to a later commit.

## Evidence

- `benchmarks/stage84_inventory.json`: original file inventory, hashes, definitions.
- `benchmarks/stage84_reproduction.json`: baseline experiment logs and missing-data errors.
- `benchmarks/stage85_stress.json`: all 56 cases, source and pipeline hashes,
  predictions, artifact hashes, runtime versions and stdout/stderr.
- `benchmarks/verification.txt`: local automated test transcript.
- `docs/STAGE84_AUDIT.md`: architecture and reproducibility audit.
- `docs/STAGE85_PROTOCOL.md`: dataset format, commands and completion gates.

## Limitations and open gates

Stage 85 photographic generalization is **pending**, not completed. No real
photographs or human-confirmed annotations were available in the repository.
Stage 84's 6 repeated photo runs / 48 archived fingerprints cannot be independently
reproduced here. The source checkpoint is preserved unchanged.

Results evaluate class presence only. They do not measure boxes, instance counts,
complex object identities, or physical camera angle invariance. Affine transforms
are simulations. Repeated variants are correlated and do not increase independent
capture count. Confirmation/source-kind metadata is declarative, not authenticated.

The legacy camera algorithms and thresholds remain unchanged. There is no external
pretrained model, training claim, private-memory migration or deployment.

## Continuation instructions

1. Start from this branch/PR; read this file and both audit/protocol documents.
2. Re-run `python -m unittest discover -s tests -v` after code changes.
3. Obtain three or more independently captured photos across physical lighting
   and viewpoints; label them before inspecting predictions, verify their hashes,
   then evaluate using `generalization.py`. Keep private photo files out of git.
4. Inspect photo failures by lighting, angle and capture group. Keep held-out
   capture groups separate from threshold tuning. Do not inflate capture counts
   with transforms or reruns.
5. Next algorithm milestone: reproduce a photographic contrast/size/aspect-ratio
   failure, implement an opt-in correction, compare old and new on held-out
   photographs and these synthetic controls. Do not tune solely to this tiny suite.
6. Later: correct localization/region correspondence with labelled boxes, then
   evaluate repeated instances, clutter and occlusion.
7. Inspect remote CI runs for this branch. Preserve evidence and update this file
   before the next execution limit. Keep historical code/checkpoints and model
   independence intact.

## Stage 86 — grouped datasets and error diagnostics

Implemented/tested/measured: reproducible capture/content component splits,
exact/pixel/near-duplicate leakage audit, pre-inference full-dataset validation,
selected-split evaluation, multi-label confusion matrices and false-positive /
false-negative examples. Added the required architecture/roadmap/status/benchmark/
limitations/integration/release/continuation documents and development ledger.

31 tests passed; `benchmarks/stage86_tests.txt` preserves the transcript.
`python scripts/benchmark_stage86.py --output NEW_REPORT.json` reproduces
`benchmarks/stage86_generalization.json`: 7 sources, 56 executions, 42 class-set
matches, 14 mismatches and no detected cross-split leakage after grouped assignment.
This is still synthetic evidence. Split metadata does not imply model training.
The near-duplicate audit conservatively groups blank/tiny-circle controls; it is
not a validated identity classifier. Approximate ratios are not class-stratified.

Next executable milestone: opt-in structured box/mask localization API, independent
adaptive segmentation experiment, IoU matching and parity against the legacy engine.

## Experimental localization API milestone (Stage 90 roadmap work)

Implemented/tested/measured: opt-in structured geometric boxes and masks,
deterministic instance IDs, EXIF-aware source coordinates, unchanged extracted
hull math, baseline parity, independent adaptive local mean/variance segmentation,
one-to-one class-aware box matching and mask/box IoU. The new API bounds JPEG/PNG
input by actual bytes/pixels and optional permitted root. It exports a local JSON
report, stroke/grouped masks and overlay; no camera or memory access is automatic.

42 automated tests pass (see `benchmarks/localization_tests.txt`). Legacy labels
and segmentation mask hashes match on all seven generated control/stress fixtures.
A three-object scene and repeated-category instances are localized in unit tests.
An installed development package (`seye-independent` 0.1.0.dev90) was tested from
outside the checkout on Linux using existing Pillow; no clean offline dependency
installation or phone/Windows validation is claimed.

`benchmarks/localization_comparison.json`: 14 generated runs, baseline TP=11,
FP=2, FN=7 versus adaptive TP=14, FP=2, FN=4 at box IoU≥0.5. The difference comes
from a generated faint scene. Both still fail clutter and have a scale error.
These correlated synthetic probes do not establish photographic accuracy;
adaptive remains experimental and opt-in, and Stage 90–99 is not complete.

Next concrete task: versioned instance/segmentation annotation schema and
multi-image localization evaluation (including negatives, multiple same-class
objects, reviewed boxes and source-to-processed coordinate validation), followed
by contour/noise/merge-split experiments against fixed baselines. Propagate bounded
ingestion into the legacy evaluator before accepting untrusted datasets. Obtain
reviewed independent photographs in parallel; do not fabricate them.
