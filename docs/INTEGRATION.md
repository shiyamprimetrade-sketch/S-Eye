# Integration status

Current stable compatibility surface: original `s_eye.py` and historical scripts.
New evaluation CLIs operate offline on explicit local datasets and do not modify
S-Memory or the parent S repository. `generalization.py --manifest ... --output ...`
emits versioned JSON; `dataset_tools.py audit|split` supplies dataset provenance.

The `src/seye/core/` modules establish reusable dataset and metric contracts.
The opt-in installed `seye.detection.analysis.analyze` API and `seye` CLI now
return structured geometric boxes and masks (see LOCALIZATION.md). These are not
a full recognition, visual-memory or S-Tools API. No end-to-end
main-S integration is claimed. No cloud vision service or pretrained model is used.

Future contracts must include request/schema IDs, permitted source roots, input
resource limits, errors/timeouts, coordinate conventions, source/model fingerprints,
uncertainty and memory consent. Add a test integration client before modifying S.
Camera access must be explicit and permission-controlled. Visual Q&A must cite
available detections/observations and reject unsupported semantic assertions.

Do not import legacy image scripts as Python libraries: several execute at import
and expect camera/filesystem state. Use subprocess isolation until an incremental
API migration proves equivalent behavior with regression tests.

## Versioned independent integration client

`seye.integration.service` now implements schema-1 requests with explicit
`Permissions(read_roots, write_roots, memory, training, video)` grants.
Actions: analyze, recognize (explicit prototype checkpoint), visual_question,
remember, retrieve, memory_list, train and prerecorded video. No shell, network,
implicit camera or arbitrary code tool is exposed. Symlinks resolve before root
checks; a read grant cannot create a memory database. Memory browsing/retrieval
opens the store read-only. Training and video require separate capability grants.

`bounded_handle` runs a request in a killable child process with a configurable
deadline and bounded request JSON. A timed-out call cannot undo an already committed
memory transaction; requests should use stable IDs and inspect the store before
retrying. Unsupported visual questions return null with a reason instead of
inventing a semantic answer. Supported questions count/list geometric hypotheses
or return their spatial relations, with source identity.

```bash
seye-workflow --request /path/to/request.json --output /path/to/new-response.json --read-root /path/to --write-root /path/to --allow-memory --timeout 30
```

Example request:

```json
{"schema_version":1,"request_id":"example-01","action":"analyze","image":"/path/to/image.jpg"}
```

For memory actions add `memory` with an explicit SQLite path. For recognition add
`model`; for training use `manifest` and `output` with `--allow-training`. Video uses
`video`, optional integer fps/max_seconds and `--allow-video`. The request and
response paths themselves must be inside the corresponding grants. Existing
outputs are preserved. Errors are versioned JSON, with no implied successful result.

This is a tested adapter/client contract suitable for S-Memory/S-Tools registration.
The main S repository has not been modified and no deployed S integration is claimed.


## Owner scope correction — 13 November 2026

The primary mission is visual observation of software interfaces for S: observe,
locate known visual controls, compare screens, record evidence and emit structured
signals. Human review is no longer a prerequisite for engineering continuation.
Earlier Stage 88 human-review continuation blocks are superseded by this instruction.
Stage 88 engineering acceptance is complete under the revised capture-only policy
(benchmarks/stage88_owner_acceptance.json). No labels or accuracy were invented;
representative generalization remains unvalidated and v1.0 remains incomplete.

Implemented the independent screenshot observer and scoped observe_interface action,
optional verified observation persistence, change-region signals, fixed-scale known
template matching and ambiguity rejection. 106 local tests pass; five generated UI
cases match expected statuses; four supplied screenshot same-frame probes show zero
change. See INTERFACE_OBSERVATION.md and benchmarks/interface_* evidence.
Stop after this stage checkpoint. Next Continue: Stage 89 interface-condition
diagnostics and automatic fixture ground truth, without a human-review dependency.


## Stage 90 — S visual subsystem clarification and contrast matching

README and PURPOSE.md now state the primary goal: S-Eye observes another computer
and sends grounded visual signals to S; S decides and S-Tools acts. Added opt-in
independent local binary contrast/polarity matching and bounded multiscale search;
the pixel baseline and historical algorithms remain preserved.
117 local tests pass. Frozen 75-case suite: 3/18 to 18/18 unique targets localized;
new 32-case design suite: 0/8 to 8/8. No false accepts or unsafe duplicate choices
in either generated suite. All 214 executions complete; 107/107 change oracles
match per method. These are generated engineering results, not real-application
accuracy or expert equivalence. See STAGE90_INTERFACE_MATCHING.md and
benchmarks/stage90_interface_comparison.json. Stage 90 engineering acceptance
is complete; exact-head CI must be checked independently.
Next Continue: Stage 91 independent edge-based interface-region proposals with
negative/overlap checks. OCR/code comprehension and live host interaction are
unfinished; no human-review prerequisite is imposed on engineering continuation.


## Stage 91 — template-free interface-region hypotheses

Implemented independent bounded RGB neighbor edges and eight-connected rectangular
region proposals, opt-in via region_proposals=true in observe_interface. Proposals
remain unlabeled and clickability unknown; default/template behavior is preserved.
124 local tests pass. Generated 33-case benchmark: 25 matched regions, 8 extra
proposals, 12 missed out of 37 targets at IoU >= 0.5. Outline duplicates, overlap
and low-contrast misses remain recorded. All four supplied screenshots process,
with 19/15/11/18 unlabelled hypotheses; no real localization accuracy is claimed.
See STAGE91_INTERFACE_REGIONS.md, benchmarks/stage91_regions.json and
benchmarks/stage91_uploaded_screenshots.json. Stage 91 scoped engineering acceptance
is complete; representative application validation and v1.0 remain incomplete.
Next Continue: Stage 92 ordered boundary extraction and outline-pair consolidation,
keeping nested/touching/overlap tests and the fixed Stage 91 baseline.


## Stages 92–100 batch checkpoint

Implemented and tested the bounded engineering scopes in STAGES_092_100.md:
ordered concave/hole contours; outline pairing; projection splitting; noise
suppression; explicit gap repair; source-grid boxes/stroke masks; visible-color
overlap analysis; caller-corner projective normalization; modular feature extraction.
143 local tests pass. Frozen region errors improve from TP25/FP8/FN12 to
TP25/FP0/FN12, preserving the 12 remaining misses. Four supplied screenshots
execute refined observation and 114-value feature extraction; proposal counts do
not improve. These are implementation/generated measurements, not representative
application accuracy or expert equivalence. Every stage has focused tests, a
reproducible experiment and its own implementation commit. Original comparators
and descriptor compatibility are preserved. Exact-head CI is tracked separately.
Owner requested stopping at Stage 100: wait for Continue before Stage 101.


## Stages 101–110 recognition-framework checkpoint

Implemented scoped geometric/appearance descriptors, schema-safe similarity,
prototype fitting, model-bound validation-only empirical support, unknown rejection,
ranked candidates, evidence explanations, generated evaluation and immutable dataset
revisions. Each stage has focused tests, a reproducible experiment and a commit.
166 local tests pass; exact-head CI is tracked separately. Existing models remain
compatible; no pretrained model or main-S modification is introduced.

Critical measured limit: generated held-out known recognition is 0/6, unknown
rejection 4/4; all ten decisions exceed validation radii. This is a failed
generalization result, not reliable recognition. The engineering framework is
implemented/tested; representative Stage 100–109 recognition validation remains
unfulfilled. See STAGES_101_110.md and benchmarks/stage109_experiment.json.

Owner now requests ten-stage batches: STOP at 110; wait for Continue before
111–120. Stage 111 should validate annotations/preprocessing and diagnose shift
sensitivity. Do not tune on the inspected test and present it as new held-out proof.
Version 1.0/expert vision is not complete; reaching Stage 199 is not itself release
acceptance. Human review is not required for ordinary engineering continuation.
