# Stage 88 — physical research photographs

Acquisition: 2026-11-13, ALOI (Amsterdam Library of Object Images), University
of Amsterdam. The official protocol documents real object-stage rotations and
physical changes in illumination, rather than generated image perturbations.

Sources:
- https://aloi.science.uva.nl/aloi/description.html
- https://aloi.science.uva.nl/aloi/download.html
- https://aloi.science.uva.nl/aloi/annotation.pdf
- https://ivi.fnwi.uva.nl/isis/publications/2005/GeusebroekIJCV2005/

Citation: J. M. Geusebroek, G. J. Burghouts and A. W. M. Smeulders,
The Amsterdam library of object images, IJCV 61(1), 103–112, 2005.
Copyright ISIS, University of Amsterdam (2004). Authors describe scientific use
and provide individual-object downloads. No permissive or commercial redistribution
license is asserted. Original pixels are excluded from public git; the exported
small research bundle includes attribution and is not a commercial dataset grant.

## Implemented and measured

`scripts/stage88_aloi.py` downloads three bounded official quarter-resolution PNG
archives and reads only six exact regular-file members per object, without tar
extraction. It rejects oversized/incomplete/invalid members and can enforce pinned
image hashes. All 18 decoded images are 192×144. Objects 4 (Round candle), 16 (Red
block), and 19 (Green block) retain the dataset authors' names, without converting
those names into geometric ground truth.

Each object has lighting captures l1c1, l3c1, l8c1 and orientation captures r0,
r30, r60. The camera is frontal: the stage rotates the object. This is relative
viewpoint variation, not a claim that the camera itself moved. Lighting-series
camera switches deliberately preserve object aspect; they are not extra viewpoint
examples. Separate series are not a factorial lighting-by-angle experiment.

18 source photos × 11 variants × 2 modes = 396 runs completed. Recognition
accuracy is null. Generated variants and the 396 runs are correlated observations;
there are three targets and 18 photographs, not 396 independent samples. No
threshold tuning or training was performed on this subset. Stored report lists
proposal classes, which are not semantic object identifications.

## Reproduce

```bash
python scripts/stage88_aloi.py --output /absolute/new/research-directory --expected datasets/manifests/stage88_aloi.json
python scripts/stage88_photo_stress.py --manifest /absolute/new/research-directory/manifest.json --output /absolute/new-report.json
python -m unittest discover -s tests -q
```

The checked-in manifest is a source/hash lock; its relative image paths resolve
only in the acquired bundle, not in the repository. Internet is required for
acquisition; inference and subsequent probing are local. Do not run acquisition in
routine CI: offline tests construct small in-memory tar fixtures.

## Gate and next task

The physical-capture availability gap is addressed for this narrow subset. The
Stage 88 gate still refuses completion: all 18 images lack human-reviewed supported
shape labels (36 explicit missing-label/review issues). Author object/material
annotations do not constitute circle/quadrilateral/triangle labels. A visual
inspection by this assistant does not constitute human confirmation.

Review the exported contact sheet and review template before examining predictions;
record reviewer identity, shape-presence labels, visibility rules and source hashes.
A rotated block can have a hexagonal silhouette despite quadrilateral visible faces;
define the labeling unit rather than assuming every block is a quadrilateral.
Keep targets grouped across splits, then run a locked labeled evaluation with
per-condition errors. Small black-background objects do not validate diverse
backgrounds, hands, household objects, semantic recognition or triangle recall.
Stage 88 remains open; Stage 89 has not started. v1.0 readiness remains false.
