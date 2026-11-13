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

Validation-only calibration experiment: 8 validation predictions fitted the map;
6 previously inspected generated test predictions scored it. Brier decreased from
0.437149 to 0.333333; recognition labels were unchanged. 92 local tests pass,
including a test proving test outcomes cannot alter the fitted map. This is not
a new locked or representative evaluation. Next: create a separately locked,
group-audited evaluation protocol and assess calibrated rejection without tuning
against these six test outcomes. See benchmarks/calibration_experiment.json.

Sequential instruction: complete each stage's acceptance contract and commit it,
then automatically proceed to the next stage while execution capacity permits.
Stage 86 loader/identity acceptance passed all six checks; recognition validation
is not implied. Next is Stage 87 grouped splits/leakage acceptance, then Stage 88.

Stage 87 engineering acceptance: all 14 dataset tests pass, covering deterministic
splits, encoded/pixel/brightness duplicates, transitive capture groups, pre-inference
leak rejection, immutable existing splits and machine-readable audit conflicts.
Next stage is 88: finish scale/perspective/background perturbation coverage and
record the physical-capture validation dependency. Do not skip that gate silently.

Stage 88 is now active, not complete: added opt-in scale-half, projective warp and
clutter-grid stress variants without changing the historical eight default variants.
The grid is an overlay and may occlude foreground; it is not a clean background-only
experiment. Projective warps are simulations, not physical camera captures. Recorded
21 generated cases and deterministic/input-preservation tests. Review
benchmarks/stage88_stress.json, then assess required physical capture/annotation
coverage before closing Stage 88. Do not advance to Stage 89 while its gate is open.

Owner workflow correction (2026-11-13): one stage per user Continue. Work on the
active stage, report its acceptance status/evidence, then stop. Only a subsequent
Continue starts the following stage. This supersedes earlier automatic sequential
continuation language. Do not call a blocked validation gate completed.

Stage 88 supplied-photo run uses four actual photographs, not screenshots. The
reproducible unlabelled stress driver covers eleven conditions in both modes.
Private pixels stay outside git. Physical lighting/angles are unmeasured, reviewed
labels/boxes are absent and these are different views/scenes rather than a controlled
same-object sweep. Execution and proposal counts cannot establish recognition
accuracy. Report the remaining physical validation gate explicitly before Stage 89.

Stage 88 capture gate is now executable in core/capture_protocol.py. It checks
review declarations, supported labels, distinct source hashes, at least three
same-target captures and two documented lighting/angle conditions. Declared coverage
is not recognition validation or authenticated annotation proof. The four supplied
photos lack reviewed shape labels and same-target capture metadata; no labels or
physical conditions were invented. See benchmarks/stage88_capture_gate.json.
Continue Stage 88; do not advance to 89 until its evidence gate is met. Required
input: reviewed circle/quadrilateral/triangle labels and three photographs of the
same targets across documented physical lighting and viewpoints.


Stage 88 internet-data checkpoint (2026-11-13): acquired 18 ALOI physical photos
from three objects across documented lighting and relative orientations; 396/396
unlabelled stress executions completed, 100 local tests passed. Capture availability
is addressed for this narrow subset. Stage 88 remains open because geometric labels
are not human-reviewed; no accuracy is claimed and Stage 89 has not started.
See STAGE88_INTERNET_DATA.md, datasets/manifests/stage88_aloi.json and
benchmarks/stage88_aloi_{stress,capture_gate,tests} evidence. Export contains images,
contact sheet, review template, provenance and reports; pixels stay out of git.
Next: review labels/visibility independently of predictions, lock grouped target
splits, then evaluate per-condition errors. Do not substitute object names for
shape truth or mark human review on behalf of a person.


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


## Stage 89 — interface-condition diagnostic checkpoint

Engineering acceptance complete: automatic renderer ground truth, 75-case theme/
scale/state matrix, hashes, per-condition status confusion, IoU localization,
false positives/negatives, ambiguity safety and change-count diagnostics.
112 local tests pass. Two benchmark runs produced identical reports.
75/75 executions and change oracles completed; only 3/18 unique targets localized
(15 missed), 45/75 statuses matched, no false accepts or unsafe duplicate choices.
The other 15 duplicate cases returned not-found. These are generated results,
not representative application accuracy; no human-review block is introduced.
See STAGE89_INTERFACE_DIAGNOSTICS.md and benchmarks/stage89_interface_conditions.json.
No Stage 84/88 recognition algorithm, checkpoint or main-S code changed.
Next Continue: Stage 90 independent contrast/edge processing and bounded scale
search, measured against the frozen matcher; do not skip negative/safety cases.
Version 1.0 and expert-programmer-level interface understanding remain incomplete.


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
