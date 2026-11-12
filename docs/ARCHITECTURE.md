# S-Eye architecture

S-Eye is an experimental independent visual-intelligence subsystem. The original
Stage 84 algorithms remain the baseline at `e92bb55`. No externally trained model
is part of core inference. Pillow supplies image decoding, resampling and filters.

## Current layers

- Historical camera pipeline: local contrast → grouping → filtering → geometry.
  Scripts retain their CLI behavior, checkpoint hashes and memory interfaces.
- Historical persistence: isolated runs → verified visual index; workflow/index
  locks and rollback remain in the original scripts. Private archives are absent
  from this public checkout and cannot be claimed verified here.
- Evaluation: `generalization.py` validates manifests, executes the baseline in
  disposable workspaces, records predictions/hashes and emits JSON diagnostics.
- Dataset integrity: `src/seye/core/datasets.py` computes canonical pixel hashes,
  near-duplicate descriptors and transitive capture/content components. Components
  receive indivisible train/validation/test assignments. The evaluator audits
  all splits before selecting any subset for inference.
- Metrics: `src/seye/core/evaluation.py` provides multi-label binary confusion
  matrices and explicit errors, separated by source kind, annotation confirmation,
  split and perturbation condition. It does not measure semantic object identities.
- Compatibility entry point: `dataset_tools.py` exposes the new src components
  without moving legacy scripts. No import triggers inference or private memory writes.

## Contracts

Dataset manifest schema 1 uses source-relative paths and actual SHA-256 values.
Optional `split` is one of train/validation/test. Split assignments require complete
coverage and no component spanning splits. Capture grouping is reviewer metadata.
Report schema 2 adds split provenance, error examples and per-class confusion.
Both schema versions refer to class presence, not bounding-box detection accuracy.
No report can automatically establish representative-data validation.

## Planned modular migration

Grow `src/seye/` incrementally with image, geometry, segmentation, detection,
recognition, learning, memory, scenes, video, integration, security and API modules.
Preserve root CLIs through wrappers and prove parity before migration. A directory
or planning stage number alone is not evidence that its capability exists.
