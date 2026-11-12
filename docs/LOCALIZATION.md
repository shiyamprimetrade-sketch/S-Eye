# Experimental structured localization

The opt-in API makes the existing independent geometry path usable as an image
analysis library without running camera or memory scripts. It does not replace
the historical root interface. The original hull functions were extracted unchanged;
new connected-component IDs have explicit deterministic tie-breaking.

## Use from a checkout

```bash
python analyze_image.py --image /path/to/photo.jpg --allowed-root /path/to --output-dir /path/to/new-analysis
python analyze_image.py --image /path/to/photo.jpg --allowed-root /path/to --output-dir /path/to/new-adaptive-analysis --mode adaptive
```

Use a new output directory each time. Outputs are `analysis.json`, `overlay.png`,
`mask.png` and `grouped_mask.png`. Images/overlays can contain private content;
keep them local. No visual memory record is automatically created. The output
directory is created privately on POSIX; platform permission behavior can differ.

## Install the new API/CLI

With Python 3.12 or newer, from the checkout:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install .
seye --image /path/to/photo.jpg --allowed-root /path/to --output-dir /path/to/new-analysis
python scripts/smoke_installed.py
```

On Windows activate `.venv\Scripts\Activate.ps1` in PowerShell. Windows and
Android installation are documented targets, not verified device results. The
Linux smoke installation used a virtual environment with system site packages
and already available Pillow, then installed the project with `--no-deps
--no-build-isolation`. A completely clean dependency-download install is not
claimed by that local experiment. CI installs dependencies and the package.

Distribution: `seye-independent`, development version `0.1.0.dev90`. This is not a
v1.0 release. The wheel installs the new src API and `seye` CLI; historical scripts
and dataset/evaluation commands remain available from the source checkout.

Python API with the installed package:

```python
from seye.detection.analysis import analyze
report, artifacts = analyze("/path/to/photo.jpg", allowed_root="/path/to")
print(report["objects"])
```

## Coordinate and mask contract

- `processed_box` uses `[left, top, right, bottom)` on the ≤300×400 processed grid.
- `source_box` scales the processed box into the EXIF-oriented source image; it
  does not refer to pre-orientation raw JPEG coordinates. Fractional edges are allowed.
- Boxes bound morphologically grouped components and may extend beyond the strokes.
- `mask` marks locally dark stroke pixels. `grouped_mask` marks morphology output.
  Neither is a learned filled foreground-instance segmentation or overlap solution.
- Region IDs belong to this analysis only. They are not cross-frame track IDs.
- `uncalibrated_geometric_hypothesis` explicitly replaces any invented probability.
  The API does not identify arbitrary semantic objects.

## Modes

`baseline` matches Stage 84 preprocessing/thresholds and broad labels. Tests verify
label parity and segmentation-mask hashes on all seven generated control/stress
images. Private historical photo parity cannot be checked without the original files.

`adaptive` is an independent experimental local mean/variance contrast rule using
summed-area tables. A dark pixel needs contrast greater than `max(3, 0.2×local_std)`
in a 31×31 clipped window. Morphology/classification/filtering remain the baseline.
This rule is not a learned model and has no calibrated confidence or photographic
validation. Keep it opt-in until independently captured development and test data
support a change to the default. Do not infer broad accuracy from the faint fixture.

## Evaluation

```bash
python -m unittest discover -s tests -v
python scripts/benchmark_localization.py --output /tmp/new-localization-report.json
```

The benchmark has one generated three-shape scene, six correlated conditions
(original/dim/faint/90-degree rotation/half-scale/clutter), and one blank control,
evaluated in both modes (14 runs). Ground truth comes from the generator, not
assistant/human photo labels. Class-aware box matching at IoU≥0.5 is one-to-one;
duplicate detections cannot increase true positives. The matcher supports up to
256 predictions/truth instances per side and rejects invalid coordinates/thresholds.
Mask IoU compares generated dark-stroke pixels where defined; empty/empty is null.
Clutter masks are not evaluated because grid pixels have no labelled object mask.

## Input boundaries and remaining reliability work

The new API accepts explicit local JPEG/PNG, verifies decoded format, limits the
actual input read to 32 MiB, rejects images above 20 million pixels and animated
inputs, and resolves source-root permissions before decode. No live camera access
is enabled. CLI failures exit 2; existing output directories are preserved.

These bounds do not establish a complete decoder sandbox, process timeout or crash
transaction across all output files. A disk/write failure can leave an incomplete
new directory. The historical scripts/evaluator do not inherit these new bounds.
Review RELEASE_CRITERIA.md before any release or untrusted-upload deployment.
