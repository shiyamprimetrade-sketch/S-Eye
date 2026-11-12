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
