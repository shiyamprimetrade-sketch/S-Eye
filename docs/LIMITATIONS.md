# Current limitations

- Only coarse geometric class presence is evaluated. Broad semantic object
  recognition, calibrated confidence and unknown-class performance are unvalidated.
- The baseline uses fixed contrast/area/aspect thresholds and hull simplification;
  faint and elongated shapes have demonstrated failures. A circle-like result is
  a geometric hypothesis, not object identity.
- New independently captured, reviewed photographs are unavailable. Private
  archives, historical memory and Stage 84 draft labels were excluded from git.
- Perturbations are correlated simulations. Physical viewpoints, realistic clutter,
  occlusion and segmentation/localization accuracy require appropriate annotations.
- Near-duplicate detection is conservative and incomplete: it can overgroup similar
  images or miss crops/viewpoint edits. Reviewer capture groups remain necessary.
  Split grouping reduces leakage risk; it does not certify data independence.
- Component split ratios are approximate and not class-stratified. Tiny datasets
  can lack categories in a split. Fewer than three components cannot yield all splits.
- Pairwise audit is quadratic, capped at 2,000 images pending a measured indexing
  implementation. Do not describe this as an already scalable dataset system.
- Metadata such as source kind/human confirmation is declared, not authenticated.
- Video tracking, independent learned recognition, searchable feature memory,
  end-to-end S adapters and release packaging remain future milestones.
- Historical concurrency uses Unix fcntl and remains Unix-only; new APIs/workflows have Windows CI coverage.
  Local execution is Linux Python 3.12; CI also exercises Python 3.13. No actual
  phone, live camera or Windows performance measurement is claimed.
- New API byte/pixel/format/source-root boundaries are tested. Legacy scripts
  and the evaluator do not yet inherit them. Decoder isolation, timeouts and
  atomic multi-file output transactions remain incomplete; no untrusted-upload
  deployment is validated.

S-Eye is experimental. Version 1.0 is not complete.

## Expanded subsystem limits

- Prototype and independent linear models currently trade known-class accuracy for
  unknown rejection, with no overall improvement over fixed geometry on the tiny
  inspected generated test. Fixed descriptors are not learned image representations.
  Raw softmax/distance scores are not calibrated truth probabilities.
- Convex boundaries, median denoising, morphology and a conservative projection
  splitter are experimental primitives. Concave/holed contour tracing, robust region
  merging, general overlap splitting and physical perspective invariance remain open.
- New observation memory has verified identity/transfer, but feature retrieval is
  linear and cross-session object histories are incomplete. JSONL import preserves
  old payloads; full historical-index migration has not been implemented.
- Scene relations use geometric hypotheses and overlap, not semantic understanding.
  Video uses a simple velocity/IoU tracker and one generated MP4 control, not broad
  representative tracking validation. FFmpeg is optional supporting infrastructure.
- New request deadlines kill a worker but cannot undo already committed writes.
  Full crash/decoder fault campaigns and release security review remain incomplete.
- The staged audit spans 86–199, but allocating numbers does not complete their
  goals. See tasks/stages_086_199.json and benchmarks/release_readiness.json for
  explicit missing requirements. S-Eye v1.0 remains unready.


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

## Stages 131–140: scene evidence and prerecorded frames

Implemented spatial topology, normalized relative positions, bounded alignment
clusters, one-to-one layout comparison with alternatives, registered change
hypotheses, persistent non-observation, evidence-referenced descriptions,
uncertainty records and read-only S scene APIs. Stage 140 adds a bounded local
prerecorded adapter with explicit video/read grants and sampling-grid times.
Existing algorithms and Stage 84 checkpoint remain preserved.

Measured generated scene matrix: 32 pairs / 64 frames, 28 exact event-count
contracts matched; localization at IoU 0.5: 80 TP, 0 FP, 8 FN. All four overlap
cases failed. The failures remain in the denominators. Representative real-world
scene validation is unfulfilled; Stage 139 completes its executable validation
harness only. No OCR, semantic UI identity, clickability, or expert vision claim.
Actual generated MPEG4 decode produced four frames at 0, .5, 1, 1.5 sampling-grid
seconds with unchanged source SHA-256. These are not original presentation times.

Run `python -m unittest discover -s tests -v` and
`python scripts/benchmark_stage131_140.py --stage N --output report.json`
for N=131..140. See STAGES_131_140.md and per-stage benchmark JSON/test logs.
No independently labeled new real-world scene corpus was available in this batch.

STOP at Stage 140. Next Continue authorizes 141–150: prerecorded temporal
continuity, bounded motion/tracking evaluation and performance instrumentation.
Do not start those stages before the next Continue. Release v1.0 remains incomplete.
