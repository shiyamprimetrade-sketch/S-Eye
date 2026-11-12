# Independent descriptor learning

Implemented: bounded fixed descriptors (ink occupancy, moments/aspect, color
statistics/histograms and texture), category means fitted from labeled examples,
nearest-category candidates, validation-derived distance rejection, transparent
explanations, deterministic fitting, dataset hashes, learning curves and verified
JSON model checkpoints. No pretrained weights or cloud inference is used. Prototype fitting learns
category means over independently engineered fixed descriptors. A separate seeded
linear softmax classifier now trains its weights and biases with explicit SGD;
it is one learned output layer, not deep vision or learned image representations.

`seye.learning.dataset.train(manifest)` verifies assigned train/validation/test
capture/content groups, fits only training rows, uses validation distances to set
rejection radii and evaluates test rows separately. Unknown samples are never fitted
as known categories. `grouped_classification_split` assigns indivisible content/
capture components within label strata; it refuses insufficient independent groups.
Source kind and annotation status must remain explicit. Synthetic independence of
parameters is not proof of representative photographic independence.

A classification manifest uses schema 1 and images with id, relative path, actual
SHA-256, label, capture_group, split, source_kind and annotation_status. Label
`__unknown__` is reserved for rejection evaluation. Feature version and dimension
must match between training and inference. Checkpoints have a canonical checksum;
wrong-version, nonfinite or modified payloads must be rejected. Existing checkpoints
are not overwritten by default. Candidate distances are not probabilities and the
model does not claim calibrated confidence.

## Reproduce the controlled experiment

```bash
python scripts/benchmark_independent_system.py --output /tmp/new-system-experiment.json
```

This generates the dataset locally, records manifest identities/splits, fits a
model, saves/restores it, compares it with fixed geometry, measures memory retrieval,
scores annotated localization and decodes/tracks a generated MP4. FFmpeg/ffprobe
are optional supporting video decoders/encoders, not recognition systems. The
experiment requires them; image/learning/memory modules work without them.

The initial experiment is preserved in benchmarks/independent_system_initial.json.
Its held-out test contained three known-category and three generated unknown-cross
images. The prototype rejected all six: known correct 0/3, unknown rejected 3/3.
This exposes excessive rejection/generalization failure, not successful recognition.
No threshold has been tuned using those test labels. Subsequent results must retain
the fixed source/split protocol or explicitly identify a new exploratory experiment.
The final current report and fixed-baseline comparison are in
benchmarks/independent_system.json. Representative photo validation remains missing.

The saved generated-data checkpoint is a research artifact, not a general hand,
furniture or text classifier. Broader labels require new representative training,
validation and locked test sets. Overfitting reports and learning curves describe
these tiny generated data only. Probability calibration, learned representations,
stronger models and realistic unknowns remain open research requirements.

## Seeded independent SGD comparison

`seye.learning.dataset.train_linear` initializes linear weights with a local seed,
trains cross-entropy with explicit SGD, saves training/validation loss curves and
uses known validation scores for a rejection threshold. It never fits test labels
or pretrained weights. Prototype and linear checkpoints share the checksum/version
contract; inference dispatches by the explicit model method. Raw softmax scores
are uncalibrated; reported confidence probability stays null.

The fixed experiment used 120 epochs, learning rate 0.1 and seed 91, chosen before
its SGD test evaluation. On the same six previously inspected generated test items,
the linear classifier got 3/3 known categories and rejected 0/3 unknowns. Prototype
learning got 0/3 known and rejected 3/3 unknowns; fixed geometry and both learned
methods scored 3/6 overall. Thus no overall accuracy improvement is established.
This comparison is exploratory, not a new locked final test. Both generated-data
checkpoints are preserved under checkpoints/generated_*_v1.json, together with
learning curves and confusion reports in benchmarks/independent_learning_comparison.json.

The next recognition task is validation-only rejection/calibration development,
followed by a separately generated and locked group-audited test protocol and
representative reviewed photographs. Do not tune to the six test labels above.
