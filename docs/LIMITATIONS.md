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
- Existing concurrency uses Unix fcntl; Windows compatibility is not established.
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
