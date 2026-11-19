# Offline memory, scenes and prerecorded video

## Observation memory

`seye.memory.store.Memory` uses a private SQLite database with an S-Eye application
ID, canonical content-derived observation IDs, checksums, transactions and explicit
verification. It refuses unrelated databases. New descriptor observations preserve
feature version, source provenance and analysis. Identical records deduplicate.
Search is an exact linear descriptor scan; no large-scale vector index is claimed.

`put/get/search/recent/verify/export/import_file/retain` expose persistence,
retrieval, browsing, checksums, verified transfer and explicit retention. Export
uses exclusive atomic JSON publication. Invalid imports are validated before writes;
transaction failures roll back. Read-only opens use SQLite read-only mode and do
not initialize or modify stores. Corruption is detected; recovery requires a known
verified export, not invented reconstruction of lost information.

`import_legacy_jsonl` wraps each old record verbatim with source-file identity and
line provenance. Missing historical descriptors remain null and are not invented
or searchable. The source file is unchanged. It does not replace the historical
visual_memory_index or migrate private archives automatically. JSONL formats are
supported; a separate full legacy-index migration remains future work.

## Geometric scenes

`seye.scenes.relations.inventory` returns evidence-class inventories, left/right/
above/below relations and an explicit geometric-hypothesis description.
`compare` matches one-to-one by class and box overlap to report appeared/missing
regions and similarity. Missing hypotheses are not proof that a semantic object
was removed. General scene grouping and real-world scene validation remain open.

## Prerecorded video

`seye.video.ingestion.analyze_video` accepts explicitly permitted local MP4/MOV/
MKV/AVI files and uses optional FFmpeg/ffprobe executables only for container/frame
handling. It never imports an external recognition model. Input dimensions, file
size, sample rate, sampled duration, frame count and subprocess timeouts are bounded.
Frames are downscaled, analyzed by S-Eye and passed to its independent tracker.

Tracking uses class-aware IoU, deterministic IDs, constant-velocity predictions
and bounded missed-frame retention. Reports preserve sampled observations and
per-track first/last-seen/count summaries. Timestamps belong to a resampled fixed
rate grid, not original presentation timestamps. Reports can be persisted as
atomic workflow responses. No live camera or continuous streaming service is claimed.
Crossings, rapid motion, long occlusion and segmentation failures can switch IDs.

The generated MP4 benchmark covers one moving circle over six sampled frames;
identity switches and frame misses are explicitly measured. Unit tests cover
repeated categories, short occlusion, expiry and timestamp rejection. These do not
establish representative multi-object video accuracy. Actual Android/Windows
performance and robust adversarial decoder containment remain unverified.
