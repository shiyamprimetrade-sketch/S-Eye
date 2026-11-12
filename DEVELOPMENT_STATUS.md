# S-Eye development status

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
  Remote CI outcome is pending until a run is observed on the published commit.

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
