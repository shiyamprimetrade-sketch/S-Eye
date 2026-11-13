# Benchmark evidence and protocols

| Experiment | Sources/cases | Result | Interpretation |
| --- | --- | --- | --- |
| Historical rotation stress | 4 generated classes × 5 angles | 20/20 | Reproduced original experiment; not photographs |
| Historical geometry challenge | 6 generated objects | Six expected labels | Reproduced baseline |
| Historical uncertainty / borderline | 9 / 8 rule cases | 9/9 and 4/8 | Borderline weakness remains exposed |
| Stage 85 camera controls/stress | 7 generated images × 8 conditions = 56 | 56 executed; 42 class-set matches, 14 mismatches | Faint triangle missed 8/8; wide quadrilateral missed 6/8 |
| Stage 84 private photographs/archives | Files absent | Not reproduced | Checkpoint assertions retained as historical |
| Independent photographic generalization | 0 new reviewed photographs | Blocked on data | Never infer photo accuracy from synthetic tests |

`benchmarks/stage85_stress.json` is immutable historical evidence from the Stage 85
harness source recorded in that report. Later harness revisions must emit a new
report with new fingerprints, not overwrite old evidence. Current report schema 2
adds binary per-class confusion matrices, false-negative/positive examples and
split provenance. Matrices cover successful executions only; pipeline failures
are separate and remain in attempted-case/exact-match denominators.

Run `python -m unittest discover -s tests -v` for regression checks. See
STAGE85_PROTOCOL.md and DATASETS.md for reproducible dataset/evaluation commands.
Report hardware/software, source counts and capture conditions. Future model
training must compare fixed baselines on held-out capture groups, with dataset
versions and learning curves. No synthetic-only experiment validates general vision.

## Opt-in localization and adaptive segmentation experiment

Reproduce `benchmarks/localization_comparison.json` with:
`python scripts/benchmark_localization.py --output NEW_REPORT.json`.

One generated three-object scene, six correlated conditions and one blank control
were evaluated in both modes, 14 runs total. Class-aware one-to-one box matching
uses IoU≥0.5. Across the six scene conditions (18 expected instances per mode),
baseline measured TP=11 / FP=2 / FN=7; adaptive measured TP=14 / FP=2 / FN=4.
Both modes detected/localized all three shapes in original, dim and 90-degree
rotation cases. Adaptive recovered three faint shapes missed by baseline. Both
modes still made a class error at half scale and failed the clutter scene.

This is an exploratory generated comparison, not an independent test-set accuracy
or proof of improvement on photographs. Adaptive mode remains opt-in. Stroke mask
IoU is 1.0 on the nominal generated scene for both modes; this is not filled-object
segmentation validation. See per-case results, labels, source/code hashes and
single-host wall timings in the report. No Android, Windows or live-video rate
is implied. Installed-package smoke evidence is in `benchmarks/install_smoke.json`.

Historical source pinning: the Stage 86 report corresponds to implementation commit
`1535578`; the localization report corresponds to `bc2cc54`. Later validation-only
fixes do not rewrite those reports. CI regenerates new artifacts for each new code
head, with that run's evaluator/support fingerprints.

## Uploaded real-input probes

See REAL_INPUT_PROBES.md and benchmarks/uploaded_input_probe.json. Five supplied
inputs are one photograph and four screenshots, not five camera photographs.
Default probing attempts 40 runs (original repeats plus simulated dim/rotation,
two modes). Report source kinds, run completion and prediction/mask repeatability
separately. No recognition or localization accuracy is calculated without truth.
The uploaded pixels remain outside the public repository.

## Independent system experiment

`benchmarks/independent_system.json` is produced by
`python scripts/benchmark_independent_system.py --output NEW_REPORT.json`.
It preserves generated classification manifests/splits, both actual fitted models,
loss curves, per-category/unknown confusion, checkpoint equivalence, memory retrieval
and export/restore checks, annotated box/mask experiments, an encoded/decoded MP4
and scoped single-host performance/storage observations. Source module hashes are
recorded. The first unsuccessful prototype-only run is retained separately.

The locked-for-this-exploratory-comparison six-item generated test contains three
known shapes and three unknown crosses. Prototype: known 0/3, unknown rejected 3/3.
Independent SGD: known 3/3, unknown rejected 0/3. Fixed geometry and both learned
methods score 3/6 overall. This is a tradeoff, not a demonstrated overall improvement
or representative recognition accuracy. The test was inspected during development;
a new separately locked and audited protocol is required for final evaluation.

Memory: 28 generated training observations, top-1 same-category retrieval 3/3 on
the three generated known test queries; all 28 observation checksums and verified
export/restore pass. No realistic large-scale retrieval quality is established.
Video: one generated moving circle, six frames at resampled 2 fps, zero identity
switches and no frames missing exactly one track. Crossings/complex occlusion and
real video remain unvalidated. Descriptor-only timing excludes image decode and
feature extraction; no Android/Windows/device throughput claim is made.


Stage 88 internet-data checkpoint (2026-11-13): acquired 18 ALOI physical photos
from three objects across documented lighting and relative orientations; 396/396
unlabelled stress executions completed, 100 local tests passed. Capture availability
is addressed for this narrow subset. Stage 88 remains open because geometric labels
are not human-reviewed; no accuracy is claimed and Stage 89 has not started.
See STAGE88_INTERNET_DATA.md, datasets/manifests/stage88_aloi.json and
benchmarks/stage88_aloi_{stress,capture_gate,tests} evidence. Export contains images,
contact sheet, review template, provenance and reports; pixels stay out of git.
Next: review labels/visibility independently of predictions, lock grouped target
splits, then evaluate per-condition errors. Do not substitute object names for
shape truth or mark human review on behalf of a person.


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


## Stage 89 — interface-condition diagnostic checkpoint

Engineering acceptance complete: automatic renderer ground truth, 75-case theme/
scale/state matrix, hashes, per-condition status confusion, IoU localization,
false positives/negatives, ambiguity safety and change-count diagnostics.
112 local tests pass. Two benchmark runs produced identical reports.
75/75 executions and change oracles completed; only 3/18 unique targets localized
(15 missed), 45/75 statuses matched, no false accepts or unsafe duplicate choices.
The other 15 duplicate cases returned not-found. These are generated results,
not representative application accuracy; no human-review block is introduced.
See STAGE89_INTERFACE_DIAGNOSTICS.md and benchmarks/stage89_interface_conditions.json.
No Stage 84/88 recognition algorithm, checkpoint or main-S code changed.
Next Continue: Stage 90 independent contrast/edge processing and bounded scale
search, measured against the frozen matcher; do not skip negative/safety cases.
Version 1.0 and expert-programmer-level interface understanding remain incomplete.
