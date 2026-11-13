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

- Opt-in localization: `src/seye/detection/analysis.py` returns deterministic
  geometric objects, half-open boxes, source coordinate mapping and mask artifacts.
  Baseline geometry is preserved; adaptive segmentation is a separate experiment.
- Image ingestion: `src/seye/image/ingestion.py` enforces explicit local source,
  optional permitted root, decoded format, byte and pixel limits for the new API.
- Installed CLI: `seye` and checkout wrapper `analyze_image.py` expose private local
  reports/overlays, leaving historical camera/memory interfaces available.

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

## Expanded independent subsystems

- Instance annotations: bounded reviewed/draft/generator manifests, source/box/mask
  identity and per-partition localization scoring (`detection/annotations.py`).
- Recognition/learning: bounded independent descriptors, category-mean prototypes,
  seeded SGD linear classifiers, explicit candidate/explanation/rejection contracts,
  canonical model checkpoints and split-audited dataset experiments. Fixed descriptor
  learning is not deep representation learning (`recognition/`, `learning/`).
- Memory: checksum-verified private SQLite observations, read-only retrieval/browsing,
  exact descriptor scan, transaction-safe import, lossless JSONL migration and retention
  (`memory/store.py`). Historical stores remain unchanged.
- Scenes: geometric inventories, relative positions and one-to-one scene changes
  (`scenes/relations.py`). No semantic scene narrative beyond evidence.
- Video: optional FFmpeg ingestion plus S-Eye's own velocity/IoU tracker, bounded
  occlusion retention and track summaries (`video/`). No external recognition model.
- Integration: schema-1 request adapter, explicit root/capability grants, killable
  request deadlines and evidence-grounded geometric queries (`integration/`).
- Deployment: installed `seye` and `seye-workflow` entry points. Development wheel
  builds and outside-checkout installation smoke tests do not constitute a v1 release.

The stage registry spans every number 86–199 with explicit open requirements.
A release audit refuses final completion while required evidence is missing.


## Owner scope correction — 13 November 2026

The primary mission is visual observation of software interfaces for S: observe,
locate known visual controls, compare screens, record evidence and emit structured
signals. Human review is no longer a prerequisite for engineering continuation.
Earlier Stage 88 human-review continuation blocks are superseded by this instruction.
Stage 88 engineering acceptance is complete under the revised capture-only policy
(benchmarks/stage88_owner_acceptance.json). No labels or accuracy were invented;
representative generalization remains unvalidated and v1.0 remains incomplete.

Implemented the independent screenshot observer and scoped observe_interface action,
optional verified observation persistence, change-region signals, fixed-scale known
template matching and ambiguity rejection. 106 local tests pass; five generated UI
cases match expected statuses; four supplied screenshot same-frame probes show zero
change. See INTERFACE_OBSERVATION.md and benchmarks/interface_* evidence.
Stop after this stage checkpoint. Next Continue: Stage 89 interface-condition
diagnostics and automatic fixture ground truth, without a human-review dependency.
