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
