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
