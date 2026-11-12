# Engineering status

Scientific status vocabulary:

- **Implemented**: working source code exists.
- **Tested**: specified automated tests passed.
- **Measured**: a reproducible experiment produced quantitative results.
- **Validated**: demonstrated on representative independent test data.
- **Experimental**: reliability not established.
- **Blocked**: a named required input or environment is unavailable.

Historical baseline: `e92bb55`, Stage 84. Active branch:
`development/stage85-generalization`. Development PR:
https://github.com/shiyamprimetrade-sketch/S-Eye/pull/1

## Stage 85

Implemented/tested/measured: isolated multi-image class-presence evaluator,
56-case synthetic benchmark and historical regression checks.
Remote CI passed at `111a8c3` on Python 3.12 and 3.13:
https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43251020390
Photographic generalization is blocked on new reviewed captures; not validated.

## Stage 86 dataset integrity and error analysis

Implemented: src dataset/metric modules, deterministic capture/content grouping,
train/validation/test split allocation, exact/pixel/near-duplicate leakage checks,
selected-split evaluation and multi-label confusion/error reports.
31 automated tests passed. The grouped 56-case synthetic benchmark retains
42 matches and 14 errors; see benchmarks/stage86_* and DEVELOPMENT_STATUS.md.
Remote CI passed at `1535578` on Python 3.12/3.13:
https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43252638455
Near-duplicate heuristics are experimental.
No model training or held-out recognition validation is claimed.

## Experimental localization API (Stage 90 roadmap work)

Implemented/tested/measured: baseline-parity localization, source/processed boxes,
stroke masks, deterministic object IDs, bounded input, optional independent adaptive
segmentation, box/mask IoU and one-to-one detection matching. A development package
and installed CLI smoke test run outside the checkout. 42 tests pass. The 14-run
generated benchmark measures baseline TP/FP/FN=11/2/7 and adaptive=14/2/4.
CI passed at `bc2cc54` on Python 3.12/3.13, including installation and both
benchmarks: https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43254093560
This does not validate photographic recognition or complete Stage 90–99.

## Next substantive task

Implement versioned instance/segmentation annotation validation and multi-image
localization evaluation; test coordinate transforms, negatives and repeated classes.
Then evaluate contour/noise/merge-split improvements against fixed baselines. Extend
bounded image ingestion into legacy evaluation paths before untrusted use. Obtain
reviewed independent photographic captures for validation. Broader recognition,
learning, video, memory retrieval and S integration remain roadmap work.

Version 1.0 is not complete; see RELEASE_CRITERIA.md and LIMITATIONS.md.

## Final audit-report correction

The audit command now saves machine-readable exact-byte duplicate conflicts;
normal evaluation and split creation still reject byte duplicates. A CLI regression
checks both behaviors. See benchmarks/final_verification.txt for the current local
suite; inspect the latest branch check run before extending earlier CI claims.

## Supplied-input probe

One uploaded photograph and four screenshots were processed in 40 runs across
baseline/adaptive modes, original repeats and simulated dim/rotation. All runs
completed; all 10 original image/mode pairs repeated the same predictions and
mask pixels. The complete suite now has 51 passing tests. These are execution/
repeatability measurements, not recognized hands/text or photographic accuracy.
See REAL_INPUT_PROBES.md and benchmarks/uploaded_input_probe.json. Private uploaded
pixels/overlays are absent from git. Reviewed labels/boxes remain required.

## Current continuation — expanded independent system

81 tests pass locally. New implementation covers versioned instance annotations,
independent descriptor/prototype and seeded SGD training, verified saved checkpoints,
private transactional observation memory and retrieval, geometric scenes,
prerecorded MP4 ingestion/tracking, and permission/deadline-scoped integration CLI.
See benchmarks/system_verification.txt, independent_system.json and LEARNING.md.

| Roadmap area | Current evidence | Still required |
| --- | --- | --- |
| 86–89 | Dataset identity, grouped splits, errors and real-input probes | Representative shape captures and complete perturbation coverage |
| 90–99 | Annotation scoring, adaptive/edge/morphology/split primitives and boxes/masks | General contours/merge/overlap and physical-perspective validation |
| 100–119 | Descriptors, prototype/SGD fitting, unknown rejection, candidates, curves, saved/restored checkpoints | Calibrated uncertainty, stronger learned features, representative known/unknown test |
| 120–139 | Verified memory, retrieval/migration/export, geometric relations and scene changes | Scalable indexing, cross-session histories, realistic retrieval/scenes |
| 140–159 | Actual controlled MP4, tracking/occlusion tests, scoped host timing/storage | Real tracking/crossings, cache/CPU/index profiling and Android/Windows measurements |
| 160–179 | Versioned scoped client, deadlines, installed workflow CLI, reports and annotation templates | Main-S registration, full user configuration and interactive annotation/usability review |
| 180–199 | Boundaries, atomic storage/rollback tests, CI and development packaging/readiness audit | Full fault/security review, representative release evidence and unmet mandatory gates |

All numbers 86–199 have explicit objectives/open requirements in
`tasks/stages_086_199.json`. No stage is marked complete merely by allocation.
The release audit returns `release_ready: false`.

Measured recognition tradeoff: on six inspected generated test items, prototypes
get known=0/3 and unknown rejected=3/3; independent SGD gets known=3/3 and unknown
rejected=0/3. Fixed geometry and both learned methods total 3/6. This is a negative
research result for overall improvement. Memory retrieval is 3/3 on generated
known queries with 28 verified/restored records. One six-frame MP4 has zero ID
switches/misses. None of these tiny controls validates real-world general vision.

Next executable priority: develop uncertainty/rejection using only development and
validation data, then run a new locked group-audited test and representative photos.
Continue the explicit unfinished engineering items (contour topology, region merge/
overlap, scalable memory/history, richer tracking and security fault campaigns).
Do not replace models with pretrained systems or declare v1.0 from passing CI.
