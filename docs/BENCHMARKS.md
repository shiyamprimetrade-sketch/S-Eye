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
