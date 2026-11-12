# S-Eye current engineering status

Historical baseline: Stage 84, `e92bb55`. Active development branch:
`development/stage85-generalization`. PR: https://github.com/shiyamprimetrade-sketch/S-Eye/pull/1

Latest implementation checkpoints:

- `b64fafc`: instance/mask annotations and independent descriptor/prototype learning.
- `1844b07`: actual seeded SGD training, restored generated-data checkpoints and
  honest model comparison.
- `0e47ca0`: verified memory, geometric scenes, prerecorded video, permissioned/
  deadline-scoped workflows, all-stage registry and release audit.

## Implemented, tested and measured

81 local tests pass. See benchmarks/system_verification.txt. Current CI must be
checked against the exact published branch head, not inferred from older runs.

| Area | Executable implementation and evidence |
| --- | --- |
| Generalization | Hash-bound multi-image loading, capture/content splits, leakage checks, class confusion/error reports and real-input probes |
| Localization | Versioned source-coordinate instances and binary stroke masks, review partitions, IoU/one-to-one metrics, baseline parity, adaptive segmentation and experimental edge/denoise/morphology/projection primitives |
| Independent learning | Fixed descriptors, fitted prototypes, seeded from-scratch linear SGD, curves, candidates, unknown rejection and verified saved/restored research checkpoints |
| Memory/scenes | Private verified SQLite observations, exact retrieval, read-only browsing, transactional transfer, legacy JSONL preservation, retention, geometric relations and scene changes |
| Prerecorded video | Actual local MP4 decode, sampled timestamps, independent velocity/IoU tracking, IDs, short occlusion retention and track summaries |
| Integration/deployment | Versioned request client, explicit file/capability grants, killable deadlines, evidence-grounded geometric questions, installed workflow CLI and development wheel |
| Reliability/release | Input/root/format bounds, corruption/rollback/migration tests, atomic files, CI, source audit, repeat-build experiment and executable v1 readiness gate |

## Measured results and failures

On six previously inspected generated test items:

| Method | Known categories correct | Unknown inputs rejected | Total correct |
| --- | --- | --- | --- |
| Prototype | 0/3 | 3/3 | 3/6 |
| Independent SGD linear | 3/3 | 0/3 | 3/6 |
| Fixed geometry | See per-item benchmark | See per-item benchmark | 3/6 |

No total accuracy improvement or representative recognition validation is established.
The models trade known correctness against unknown rejection. Do not tune to these
six test labels. Actual model parameters, source/data hashes, curves and results
are in checkpoints/generated_*_v1.json and benchmarks/independent_system.json.

Memory: 3/3 same-generated-category retrieval queries, with 28 observations verified,
exported and restored. Video: one generated moving-circle MP4, six sampled frames,
zero ID switches and no missing-track frames. These are tiny controls, not broad
retrieval/video validation. Installed API/workflow smoke passed outside the checkout.
Two frozen-source development wheel builds were identical; no v1 release was issued.

## Stages 86 through 199

Every number has an objective/evidence path/open requirement in
`tasks/stages_086_199.json`. The allocation is a tracking mechanism, not proof of
completion. No stage is marked complete merely by number or successful execution.

Open engineering includes calibrated confidence/rejection, general contour topology,
merge/overlap separation, perspective validation, scalable indexing, cross-session
object histories, richer scenes/tracking, cache/CPU profiling, user configuration/
annotation usability, full crash/security campaigns and actual Android/Windows
measurements. Reviewed representative photo/unknown/scene/video datasets are missing.
The supplied inputs comprise one photograph and four screenshots, with no confirmed
instance boxes; their 40-run probe does not establish photographic recognition.

## Next executable work

Develop uncertainty/rejection using development and validation data only. Then
create a new locked group-audited test protocol and evaluate representative reviewed
annotations. Continue independent remaining engineering requirements from the stage
registry while validation data is absent. Preserve Stage 84 and independent models.

Version 1.0 is **not complete**. `benchmarks/release_readiness.json` records false
readiness. `scripts/release_audit.py --require-release` refuses unmet mandatory gates.
Main-S registration/deployment, pretrained replacement and a production release
have not been performed.

## Cache/configuration continuation

Windows and Linux CI at `acf5cbe` passed on Python 3.12/3.13, including the preceding
81 tests, installation/video, experiment reports and development wheels.
The subsequent continuation adds strict versioned configuration/migration, granted
batch recognition, bounded descriptor LRU and transitive geometric proximity groups.
Current local results are in benchmarks/cache_phase_tests.txt and cache_experiment.json;
new-head CI must be checked separately. See CONFIGURATION_PERFORMANCE.md.

The repeated-input cache experiment measured identical descriptors, 19 hits/1 miss,
3,197 estimated Python bytes and a 6.66× observed descriptor-path wall-time ratio
on one generated image. This is not full vision acceleration or an Android claim.

Latest local full regression: 87 tests passed, including cache/config/batch/grouping
and corrected physical JSONL provenance line numbers. See
benchmarks/final_system_verification.txt. Current code/check runs must be inspected
for the exact branch head; the earlier 81-test Windows/Linux run remains its own
historical proof. The source tree remains experimental and v1.0 readiness is false.
