# Independent descriptor learning

Implemented: bounded fixed descriptors (ink occupancy, moments/aspect, color
statistics/histograms and texture), category means fitted from labeled examples,
nearest-category candidates, validation-derived distance rejection, transparent
explanations, deterministic fitting, dataset hashes, learning curves and verified
JSON model checkpoints. No pretrained weights, cloud inference, neural-network
training or learned feature representation is claimed. This is prototype learning
on independently engineered descriptors.

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
