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
