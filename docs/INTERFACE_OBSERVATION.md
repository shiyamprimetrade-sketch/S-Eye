# S-Eye as the visual input subsystem of S

Owner clarification (13 November 2026): S-Eye's primary use is observing software
interfaces for S, the programming system. It should observe, compare, record and
emit evidence that S can interpret. Human label review is not required to continue
engineering. Earlier instructions making human review a prerequisite for Stage 88
continuation are superseded. Independent experimental evidence remains required;
removing a review requirement does not create recognition accuracy.

## Implemented interface-observation contract

Action `observe_interface` in the existing schema-1 scoped integration adapter:

```json
{
  "schema_version": 1,
  "request_id": "editor-frame-002",
  "action": "observe_interface",
  "image": "/permitted/screens/current.png",
  "previous": "/permitted/screens/previous.png",
  "templates": [{"name": "run_button", "path": "/permitted/templates/run.png"}],
  "stride": 4,
  "min_similarity": 0.97,
  "memory": "/permitted/memory/observations.sqlite3"
}
```

`previous`, `templates`, and `memory` are optional. Invoke through the existing
`seye-workflow` CLI with explicitly granted read/write roots, and `--allow-memory` when
persisting. Consult `seye-workflow --help` for the full request/response options.
The main S repository is unchanged; this adapter is executable independently.

Results include source hash/dimensions, changed-pixel fraction, connected changed
16-pixel tiles, source-coordinate boxes, caller-named template candidates, explicit
ambiguity/not-found results and structured signals. A resolution change emits
`viewport_changed` instead of silently resizing frames. A repeated frame emits
`pixels_unchanged`; the initial frame emits `initial_observation`.

Templates are grayscale, fixed-scale screenshot crops. Names originate from the
caller; a label `run_button` is not proof the engine understands a Run command.
A bounded eight-by-eight sample scan is followed by full-patch mean absolute error
verification. Repeated similar controls cause abstention if the two best distinct
matches have similarity within 0.01. A candidate is not proof of clickability.
Similarity is not a calibrated probability. Anti-aliasing, theme, scaling, stride
alignment and brightness can break matching. A high score is possible for unrelated
patterns; use additional state evidence before deciding an action in S.

Screenshot limits: 4 million pixels, existing 32 MiB decoder bound, eight templates,
8..256-pixel template dimensions, 50,000 searched positions per template. Templates
with grayscale standard deviation below eight are rejected. All paths must be
within grants; memory also requires a write grant and memory capability. No mouse,
keyboard, browser/OS capture, shell, network or camera action is introduced. Text
seen in screenshots is untrusted content, never an instruction to execute.

Optional memory stores structured observations with SHA-256 provenance and existing
SQLite verification. No image pixels or extracted text are stored in that record.
Memory records have no learned descriptors; similarity retrieval skips them.
`memory_list` retrieves them. Capturing screenshots remains the host/S-Tools adapter's
responsibility. OCR, code reading, application state understanding, navigation,
scroll correspondence and expert programmer equivalence remain unimplemented.

## Evidence

- 106 local automated tests pass, including changed boxes, absence, duplicate-match
  abstention, budget/contrast checks, root/memory permissions and memory round trip.
- Five generated interface cases produce five expected statuses: known/translated
  template found, absent template rejected, duplicate controls ambiguous, dimmed
  template rejected under exact matching. These are deterministic generated checks,
  not recognition accuracy across independent applications.
- Four previously supplied screenshots decode and produce zero changed pixels when
  compared with identical bytes. This only tests actual screenshot ingestion and
  repeatability; no OCR or UI recognition is measured on those inputs.
- `python scripts/benchmark_interface.py --output NEW_REPORT.json` reproduces the
  generated experiment. CI also runs it and retains the machine-readable report.

## Stage acceptance and next stage

Stage 88 engineering acceptance is complete under the owner's revised policy:
physical capture coverage exists, all eleven stress variants execute, and missing
human labels no longer prevent continuation. `assess(...,
require_reviewed_labels=False)` checks physical coverage without pretending labels
exist. The original default labeled-evaluation policy remains available for callers
that explicitly need it. Photographic accuracy stays null; representative validation
is false. The interface observer is an additional implemented/tested milestone,
not a claim that the entire interface-vision objective is finished.

On the next Continue, Stage 89 should establish automatic interface test fixtures
and machine-readable per-condition localization/change diagnostics, including
scaling, light/dark themes, repeated controls and unsupported cases. Use generated
fixture metadata as exact automatic ground truth and label it generated. Add real
application screenshot evaluations when a documented oracle is available; do not
block implementation on human review or claim unmeasured accuracy.


Stage 90 adds optional `matcher: contrast` and explicit `scales` to the same request.
The default pixel matcher is preserved. See STAGE90_INTERFACE_MATCHING.md for
contrast thresholds, bounded scale search, measured comparisons and limitations.
