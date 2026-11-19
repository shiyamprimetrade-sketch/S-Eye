# Stage 90 — local contrast and bounded scale matching

S-Eye is the visual subsystem of S for observing another computer. This milestone
improves known-control localization across supported contrast/polarity and scale
changes. The small JSON observation contract and existing pixel matcher remain
compatible; no pretrained model or main-S modification is introduced.

## Use

Add these fields to an existing schema-1 `observe_interface` request:

```json
{
  "matcher": "contrast",
  "scales": [0.75, 1, 1.25, 1.5, 2],
  "min_similarity": 0.99
}
```

These are request fields, not a complete request: supply `request_id`, `image`,
`templates` and the other required integration fields as documented in
[INTERFACE_OBSERVATION.md](INTERFACE_OBSERVATION.md). `scales` and similarity are
optional. The contrast mode defaults above are applied through the scoped S JSON
adapter. The compatibility default remains `matcher: pixel` with no scale search.
The lower-level `observe` Python function uses the same mode-specific defaults: exactly
0.99 for contrast and the historical 0.97 for pixel matching. Candidate boxes are EXIF-oriented source
pixels with exclusive right/bottom coordinates. Memory/permissions are unchanged.

The independent algorithm thresholds each grayscale candidate patch at the midpoint
of its local min/max values, compares binary structure in either polarity, and
searches the requested resized templates. Eight-by-eight sampling screens positions;
full binary patch comparison verifies surviving candidates. Cross-scale overlap
suppression groups responses to one control. Similar distinct controls cause an
ambiguous result with no actionable candidate. Similarity is agreement of binary
pixels, not calibrated probability or proof of function/clickability.

Search is bounded to five unique scales in [0.5,2], scaled dimensions in [8,256],
and 50,000 positions **across all scales per template**. A patch with luminance
range below 16 is rejected. Existing image, template-count, permission and deadline
limits remain. Unsupported configurations fail explicitly. Large screenshots may
need a larger stride or an upstream cropped viewport; crop offsets must be mapped
by the caller. No implicit downscaling or coordinate remapping is performed.

## Reproduce

```bash
python scripts/benchmark_stage90.py --output /absolute/new/stage90.json
python -m unittest discover -s tests -q
```

The comparison uses the frozen 75-case Stage 89 matrix, then 32 additional cases
from two new designs (plus/chevron), scales 0.75/1.25, two themes, new positions and
single/absent/duplicate/occluded states. Designs, scale grid, stride and exact
threshold were specified before the first execution; there is no training,
parameter search or checkpoint selection. These held-out-design probes still share
rendering primitives and are not representative independent application data.
All source/template/frame hashes and protocol identity are retained.

| Generated suite | Pixel baseline | Contrast/scale mode |
| --- | ---: | ---: |
| Frozen unique controls localized (IoU ≥ 0.5) | 3/18 | 18/18 |
| Frozen expected statuses matched | 45/75 | 75/75 |
| Additional-design unique controls localized | 0/8 | 8/8 |
| Additional-design expected statuses matched | 16/32 | 32/32 |
| False accepted candidates, both suites combined | 0 | 0 |
| Unsafe single choices on duplicate cases | 0 | 0 |
| Exact change signal/count matches | 107/107 | 107/107 |

All 214 executions completed (107 inputs per method). The frozen pixel report
reproduced Stage 89's cases and summary exactly. Contrast mode marked all 26
duplicate cases ambiguous, while the pixel baseline marked only three ambiguous
and missed the others. No claim of positive occlusion support: occluded targets
are rejection cases. CLI acceptance checks require the frozen baseline and these
generated contracts; exit success does not assert real-application accuracy.

117 local tests pass, including five new tests for polarity/scale localization,
cross-scale duplicate abstention, missing/low-contrast/off-stride cases, combined
resource budgets, invalid configuration and the scoped JSON integration. CI runs
both historical and new benchmarks and uploads their reports; inspect exact-head
CI separately. Stage 84 code/checkpoints and the Stage 88 pixel matcher are kept.

## Limits and next stage

Binary contrast loses color/texture identity. Different controls with the same
binary pattern may match; a supplied name is not independently inferred meaning.
Candidate sampling and stride can miss true matches. Unrequested scales, gradients,
noise, anti-aliasing, unfamiliar glyphs, overlap and complex backgrounds remain
unvalidated. The benchmark uses exact agreement; API defaults at 0.99 need broader
false-positive measurement. Generated success is not perfect autonomous vision.

Stage 90 engineering acceptance is complete for this scope. Next Continue starts
Stage 91: independent edge-based interface-region proposals, with automatic oracle
tests and negative/overlap cases, so S-Eye can propose regions without a supplied
crop for every control. OCR, code comprehension, actual screen capture/input and
representative application validation remain separate unfinished capabilities.
