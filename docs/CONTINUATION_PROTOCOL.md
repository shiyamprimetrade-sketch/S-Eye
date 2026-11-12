# Continuation protocol

1. Read this file, STATUS.md, DEVELOPMENT_STATUS.md, ROADMAP.md, latest ledger,
   RELEASE_CRITERIA.md and repository instructions. Inspect working-tree changes,
   active branches, PR #1 and its exact head/check runs before editing.
2. Preserve baseline `e92bb55`, every historical checkpoint and independent
   recognition path. Do not reset the project or overwrite unrelated work.
3. Establish tests with `python -m unittest discover -s tests -v`. Legacy scripts
   have local-data assumptions; do not run patch/backup scripts as setup steps.
4. Use `dataset_tools.py` for grouped splits and leakage audits; validate the full
   dataset before selecting held-out data. Do not tune on test data or fabricate
   missing labels/capture conditions.
5. Complete the next concrete task in STATUS.md, implement meaningful code, add
   tests, fix failures and run relevant benchmarks. Update scientific status as
   implemented/tested/measured/validated/experimental/blocked with real evidence.
6. Commit to `development/stage85-generalization` and update PR #1 while this
   continuation remains unmerged. Inspect remote state before every publication.
   Never force-push unrelated work or merge failing required checks.
7. Git CLI can read public refs but HTTPS push lacks credentials in this session.
   Use connected GitHub create_tree/create_commit/update_ref with an expected
   branch SHA. Preserve the full parent tree. Reconcile local and remote commits
   only after checking identical trees. Do not expose credentials.
8. Before execution limits: save code, tests, benchmark reports, branch/head/PR,
   outstanding failures, limits and the next executable task here and in the ledger.
   If publishing is blocked, preserve local work and state the exact blocker.
9. Do not claim work continued between inactive sessions. Read actual latest
   evidence on resume. Stage numbers do not establish completion.

Real photographs are needed for validation, but their absence does not block
independent architecture, annotation, localization or reliability implementation.
No sub-agents are required or authorized by this protocol.

Latest implemented continuation: grouped datasets (Stage 86) and the experimental
localization API (Stage 90 roadmap work). The exact next task is instance/mask
annotation validation and dataset-level localization evaluation; see STATUS.md.
The installed `seye` package is a development API, not a complete S-Eye release.

Uploaded-image continuation: read REAL_INPUT_PROBES.md and the uploaded-input JSON
report. Only one of the five supplied inputs is a photograph; four are screenshots.
The real-input probe is deliberately unlabelled and cannot establish recognition
accuracy. Original image bytes/overlays are private and absent from git; do not
fabricate access to them in a later session. Use new supplied bytes or report the
reproduction dependency. Continue with instance/mask annotations and unknown-rejection.

Expanded checkpoint continuation: inspect tasks/stages_086_199.json, current STATUS,
LEARNING and benchmarks/independent_system.json. Source includes independent SGD,
prototype learning, annotation evaluation, memory, scenes, video and scoped workflows.
Do not mistake these experimental implementations for completion of every phase.
The learned models trade known correctness against unknown rejection; total test
correctness has not improved over fixed geometry (3/6 on the inspected generated set).
Do not tune against those test labels. Next: validation-only rejection development,
new locked group-audited tests and representative annotations, while implementing
remaining engineering requirements recorded for each stage. The v1 release audit
must remain false until all mandatory gates are evidenced. No background work is
claimed between inactive sessions.

Published implementation references for this expansion: `b64fafc` (annotations/
prototype), `1844b07` (seeded SGD comparison), `0e47ca0` (memory/scenes/video/workflows/
stage registry and release gate). Read their exact CI runs and newest branch head
before extending claims. The local suite is 81 tests. Current STATUS.md is rewritten
around the latest implementation; older logs remain in ledger, reports and Git history.

Cross-platform reference: `acf5cbe` passed Ubuntu/Windows, Python 3.12/3.13,
installation, the preceding 81 tests and actual MP4/benchmark/build checks.
Later cache/config continuation has separate tests/reports; inspect its exact head.
Read CONFIGURATION_PERFORMANCE.md for root/capability policy and cache measurement
scope. Android hardware remains unverified; geometric proximity is not identity.

Cache/config/group implementation is saved at `bec5213`; Windows/Linux verification
is saved at `acf5cbe`. A final reliability fix preserves physical source-line numbers
when importing JSONL with blank lines and enforces integer observation schema tags.
The 87-test final transcript is benchmarks/final_system_verification.txt. Continue
from the newest head/CI; do not declare completion of stages 86–199 or v1.0 merely
from these tests. Existing learning/representative-data and engineering gaps persist.

Calibration continuation: learning/calibration.py implements independent monotonic
validation-frequency pooling, strict finite inputs and support counts. It is not
wired into inference and does not establish representative confidence. Next fit it
only on validation predictions and assess a new locked test; never calibrate on test
outcomes. Existing recognition failures and release gates remain open.
