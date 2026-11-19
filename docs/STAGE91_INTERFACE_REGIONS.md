# Stage 91 — template-free interface-region hypotheses

S-Eye can now propose rectangular visual regions without receiving a crop for
every control. It uses independently implemented RGB neighbor edges and connected
components. No model, OCR, semantic label or clickability inference is involved.
The existing template matchers and default observation behavior are preserved.

## Use through S

Add `"region_proposals": true` to a schema-1 `observe_interface` request. Templates
are optional; proposals can also accompany known-template matches and frame-change
signals. Source read permissions and optional memory permissions remain required.
No camera, host capture or input actions are introduced. See the existing
[interface contract](INTERFACE_OBSERVATION.md) for the complete request structure.

The response adds `region_proposals` and a `region_hypotheses` signal. Each region
has a stable per-frame ID, source-pixel half-open box, edge-pixel count and observed
border coverage. `semantic_label` is null and `clickability` is unknown. IDs are
not temporal track identities. `elements` continues to contain only named-template
results. Optional memory records both kinds of evidence through the existing
integrity-verified store.

A region is a hypothesis for S to inspect, not a button name or safe click target.
S must use context and additional observations to decide what a region means.
Screenshot content remains untrusted data rather than instructions.

## Independent algorithm and bounds

1. Compare each RGB pixel to its left and upper neighbors. Use the maximum channel
   difference so color-only boundaries survive equal grayscale luminance.
2. Threshold neighbor differences at 24 into a binary edge mask; avoid artificial
   image-wrap edges.
3. Traverse eight-connected edge components in deterministic scan order.
4. Retain boxes at least 12×8 pixels with observed border occupancy at least 0.75.
5. Sort by source position and return up to 128 unlabeled hypotheses.

Source coordinates are retained without rescaling; the discrete edge box can
extend one pixel beyond the visible rectangle. Decoder limits are unchanged.
Proposal processing permits four million pixels, at most 200,000 edge pixels and
10,000 components. Budget failures are explicit errors. Proposal truncation is
explicit (`truncated: true`, `complete: false`, plus total candidate count); partial
output cannot silently claim completeness. Smaller region limits are available in
the Python function. The JSON flag deliberately exposes a small fixed contract.

## Measured evidence

```bash
python scripts/benchmark_stage91.py --output /absolute/new/stage91.json
python -m unittest discover -s tests -q
```

The renderer supplies automatic region boxes before inference: two themes, two
scales, eight layouts (single/multiple/outlined/nested/overlap/noise/low-contrast/
blank), plus one equal-luminance chromatic-boundary case. No template is supplied.

| Generated localization at IoU ≥ 0.5 | Result |
| --- | ---: |
| Executions | 33/33 completed |
| Annotated regions | 37 |
| Matched regions | 25 |
| Extra proposals | 8 |
| Missed regions | 12 |

The eight extras are inner/outer outline duplicates. Overlapping controls account
for eight misses; low-contrast controls account for four. Blank/noise cases have
no proposals. This measures rectangular visual-region localization, not recognized
controls, real-application accuracy or expert programmer vision. The report includes
per-condition metrics, boxes, IoU matches, input pixel hashes and fixture identity.
Execution failures count as missed requested targets; condition groups contain only
completed cases and execution errors remain separate.

All four previously supplied screenshots completed an unlabelled proposal probe,
returning 19, 15, 11 and 18 hypotheses respectively with no truncation. Without box
oracles these counts do not measure localization success. Private pixels and text
are excluded from public git; only source hashes and execution counts are recorded.

124 local tests pass, including six new tests for localization/identity, color
edges, blank/noise/low contrast, pixel/edge/component budgets, truncation, scoped
JSON observation/memory without templates, and preserved outline/overlap failures.
Repeated generated reports are deterministic. CI runs the full suite and new
benchmark and uploads its report; exact-head CI must be checked separately.

## Acceptance and next stage

Stage 91 engineering acceptance is complete for bounded independent edge/region
hypotheses. Overlap handling, duplicate boundary consolidation, rounded/irregular
controls, text grouping, low contrast and unfamiliar application validation remain
unfinished. A component may represent a panel or icon, and nested boundaries can
produce multiple hypotheses. A sparse negative set is not proof against false
positives on complex screens.

Next Continue starts Stage 92: ordered contour/boundary extraction and pairing
inner/outer rectangular boundaries, evaluated against this frozen baseline with
nested, touching and overlapping examples. Preserve evidence rather than hiding
misses; do not turn hypotheses into semantic controls or automatic input actions.

## Cross-platform regression repair included

Stage 90 run 43404599506 passed both Ubuntu jobs but failed the Windows benchmark
step after producing the same localization/status totals. The frozen-report gate
compared encoded PNG hashes along with inference results. That is too sensitive
to platform encoder representation.

The repair retains encoded hashes as provenance, and requires both identical
semantic case results and pinned canonical image identities (RGB mode, width,
height and decoded bytes). It does not waive pixel integrity. A new test permits
only encoding-hash variation and rejects changed pixels, statuses or summaries.
`benchmarks/stage89_pixel_identities.json` pins all 75 frozen image identities;
`benchmarks/stage91_portability_regression.json` records the repaired full Stage 90
comparison. The local repaired gate passes. New Windows CI must be inspected
before claiming the cross-platform repair verified remotely.
