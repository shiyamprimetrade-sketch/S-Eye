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

Stage 91 also repairs Stage 90's representation-sensitive frozen-report gate:
Windows CI run 43404599506 failed report equality while detection totals matched.
Canonical mode/dimension/RGB identities are now pinned, encoded hashes retained,
and semantic results still required. See tests/test_benchmark_portability.py and
benchmarks/stage91_portability_regression.json. Inspect new Windows CI before
claiming remote success. Do not revert to encoded-file equality or drop pixel checks.

Stage 91 verified remote checkpoint: `165ab1d663354cce045ec690df4705d66c716e43`. All four Ubuntu/Windows Python 3.12/3.13 jobs passed, including 124 tests, the repaired Stage 90 portability gate, Stage 91 benchmark, installation, audits and artifacts. Evidence: https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43405604944 . This publication receipt changes documentation only; do not attribute the earlier CI run to a later SHA.


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

Verified Stages 92–100 checkpoint: `38062303cdc055e2cd5401d075892797e3680f70`. All four Ubuntu/Windows Python 3.12/3.13 jobs passed: 143 tests, every stage experiment, historical benchmarks, installation, audits and artifacts. https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43407859586 . Later publication receipts change documentation only; the cited run belongs to this exact SHA. Stop at Stage 100 and wait for owner Continue.


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

Verified 101–110 framework checkpoint `6417eb9305e1e18a404fa0ccb3641b9ac9146f1b`: all four Ubuntu/Windows Python 3.12/3.13 CI jobs passed, including 166 tests, ten experiments, historical checks, installation, audits and artifacts. Evidence: https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43410582280 . The known-glyph result remains 0/6 and representative recognition is not validated. This later receipt changes documentation only; the cited CI run belongs to that exact SHA. Stop at 110 and wait for Continue.


## Stages 111–120 learning and persistence checkpoint

Implemented annotation/provenance checks, explicit partitions, independently
seeded schema-bound SGD, verified inference checkpoints, reproducibility records,
overfit diagnostics, sample-count curves, baseline/ablation comparisons, separate
known/unknown regression gates and optional verified trained-observation memory.
187 local tests pass, including the legacy batch-recognition path. A predictor
import-shadowing regression caught by the full suite has been corrected.

New precommitted generated protocol: layout comparator 0/6 known and 4/4 unknown;
centered prototype 6/6 and 4/4; centered SGD 6/6 and 4/4. The representation change
accounts for the observed gain; SGD does not outperform centered prototypes here.
These are correlated synthetic captures, not representative application accuracy.
The original Stage 109 failure is preserved. See STAGES_111_120.md and
benchmarks/stage118_experiment.json. No pretrained weights, old-model replacement
or main-S change. Exact-head CI is tracked separately.

STOP at Stage 120. Wait for Continue before 121–130, beginning with observation
identity and schema-aware memory retrieval. OCR/expert vision and v1.0 remain
unfulfilled. Human review does not block ordinary engineering continuation.

Verified 111–120 checkpoint `fae018ae9ed9d96568c3334fe53d611b45d53010`: all four Ubuntu/Windows Python 3.12/3.13 CI jobs passed, including 187 tests, all ten new experiments, historical checks, installation, audits and artifacts. Evidence: https://github.com/shiyamprimetrade-sketch/S-Eye/actions/runs/43437615904 . The 6/6 known and 4/4 unknown centered-descriptor result remains generated evidence, not real-application validation. This later receipt changes documentation only; the cited CI run belongs to that exact SHA. Stop at 120 and wait for Continue before 121–130.


## Stages 121–130 visual-memory checkpoint

Implemented separate image/observation/session identities, persistent schema KD
indexes, exact packet retrieval, caller-linked histories, source-grid scene
comparison, distinct duplicate evidence, provenance audits, portable recovery
bundles, pinned dependency-aware retention, measured generated retrieval and
unlabeled scene inventories. New interface memories retain searchable packets;
legacy records stay unchanged. 210 local tests pass; exact-head CI is separate.

64-vector test: exact top3 matches exhaustive search with 7 versus 64 distance
evaluations, but full integrity/snapshot cost remains linear. Generated glyph
retrieval: 6/6 known categories top1/recall@3, 4/4 unknowns without matches under
fixed cutoff; all known queries have tied matches and no unique-object identity.
Verified recovery/retention preserves links or removes dependencies transactionally.
See STAGES_121_130.md and per-stage benchmark reports. These are controlled
engineering results, not representative application memory/identity validation.

STOP at Stage 130. Wait for Continue before 131–140. Future scene relationships
must preserve coordinate/semantic uncertainty and cannot promote caller links,
feature matches or proximity into proven object identity. Release v1.0, OCR and
expert programmer vision remain incomplete; human review does not block engineering.
