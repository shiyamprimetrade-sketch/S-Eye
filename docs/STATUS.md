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
This does not validate photographic recognition or complete Stage 90–99.

## Next substantive task

Implement versioned instance/segmentation annotation validation and multi-image
localization evaluation; test coordinate transforms, negatives and repeated classes.
Then evaluate contour/noise/merge-split improvements against fixed baselines. Extend
bounded image ingestion into legacy evaluation paths before untrusted use. Obtain
reviewed independent photographic captures for validation. Broader recognition,
learning, video, memory retrieval and S integration remain roadmap work.

Version 1.0 is not complete; see RELEASE_CRITERIA.md and LIMITATIONS.md.
