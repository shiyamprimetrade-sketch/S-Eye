# Instance and mask annotations

`seye.detection.annotations` validates schema-1 manifests in EXIF-oriented source
coordinates before inference. Instances have unique IDs, evidence category strings
and finite half-open boxes `[left, top, right, bottom)` inside the oriented image.
Each image records its actual SHA-256, capture group, source kind, annotation status
and annotator. Generator labels must use synthetic sources; draft and declared
human-reviewed labels remain separate result partitions. Review declarations are
not authenticated by the software.

Optional masks require their own SHA-256, the same oriented pixel grid and binary
values. The current metric accepts `mask_scope: dark_strokes`, matching the engine's
stroke mask. It refuses to equate this with a filled-object/instance segmentation.
If splits are present, the whole dataset is audited before subset selection.
Pipeline errors remain counted separately; they are not fabricated predictions.

```bash
python scripts/create_annotations.py --directory /path/to/images --output /path/to/images/draft.json --source-kind photograph --annotator YourName
```

This emits an **unscored template** with empty instance arrays. Empty templates
must not be scored as confirmed negative images. Inspect each image, add actual
boxes/classes, record capture groups and review status, then explicitly remove
`template_unscored` only when the manifest is ready to evaluate. Unsupported classes
such as hand are allowed as ground truth; the geometry engine's failure to predict
them is counted as missing, rather than being relabeled a success.

```bash
python scripts/evaluate_instances.py --manifest /path/to/reviewed.json --output /path/to/new-evaluation.json --mode baseline
```

Class-aware maximum-cardinality box matching at the configured IoU threshold
prevents duplicate predictions from increasing true positives. Results report
precision/recall and optional stroke-mask IoU. Generated controls, draft labels and
human-reviewed sources never mix in a summary. Representative validation remains
a scientific review gate, not an automatic consequence of having a JSON annotation.
