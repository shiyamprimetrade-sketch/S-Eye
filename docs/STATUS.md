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
Verification and benchmark results are recorded in DEVELOPMENT_STATUS.md and
benchmarks/stage86_* after execution. Near-duplicate heuristics are experimental.
No model training or held-out recognition validation is claimed.

## Next substantive task

Add an opt-in structured localization API with deterministic connected components,
explicit box coordinates, mask/box metrics and synthetic localization benchmarks.
Preserve the legacy classifier as a parity reference. Use actual captures later
to validate supported conditions. Independently continue security/resource limits
and annotation tooling while representative photos remain unavailable.

Version 1.0 is not complete; see RELEASE_CRITERIA.md and LIMITATIONS.md.
