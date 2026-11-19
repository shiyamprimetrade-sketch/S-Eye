# Dataset identity, splits and leakage

Keep schema-1 manifests as documented in STAGE85_PROTOCOL.md. `capture_group`
must join captures that should never cross splits (same scene/session/burst,
derived edits and known related images). Never use a unique filename as proof of
independence. Human-reviewed source metadata is still required.

```bash
python stage85_fixture.py /tmp/s-eye-data --stress
python dataset_tools.py split --manifest /tmp/s-eye-data/manifest.json --output /tmp/s-eye-data/split.json --seed 85
python dataset_tools.py audit --manifest /tmp/s-eye-data/split.json --output /tmp/s-eye-data/audit.json
python generalization.py --manifest /tmp/s-eye-data/split.json --split test --output /tmp/s-eye-heldout.json
```

Output paths must be unused. A split manifest is saved beside its source to
preserve relative image paths. Existing splits are never silently reassigned.
Default group ratios are 60/20/20, rounded deterministically with at least one
component per split. Require three or more independent components. Counts are
component counts; image/class balance is not guaranteed. This command allocates
subsets only; it does not train a model or establish held-out model accuracy.

Audit unions capture-group matches, encoded-byte duplicates, canonical decoded RGB
pixel duplicates and conservative near-duplicate matches into connected components.
EXIF orientation is normalized. Near matching uses aspect ratio, 64-bit difference
hash, and mean/std-normalized grayscale thumbnail MAE. It is brightness-tolerant
for tested fixtures, not guaranteed invariant. Policy thresholds, fingerprints,
links and conflicts are emitted; inspect them before trusting a split.

`audit` exits 1 and saves evidence for cross-split conflicts, including byte-identical
files. Split creation and recognition evaluation still reject exact byte duplicates. `split` refuses fewer
than three components. The evaluator validates the entire assigned dataset before
running any selected split, and rejects leaked/partial/invalid assignments. It
also rejects duplicate encoded bytes entirely, even within one subset. Deduplicate
exact files before running the evaluation. Split metadata is not evidence of a
training experiment when the algorithm has never been trained on it.

Report schema 2 separates source kind, annotation confirmation, split and variant.
Per-class 2×2 confusion counts are multi-label presence counts, not a forced
single-class confusion matrix. Unknown predictions contribute false positives.
Pipeline failures are counted separately and do not become fabricated predictions.
The report explicitly records `recognition_validation_status: not_established`.

A maximum of 2,000 files limits the quadratic audit. Crops/viewpoint changes can
escape detection and similar content can be conservatively overgrouped. Record
these as heuristic findings, not recognition or duplicate-detection accuracy.
