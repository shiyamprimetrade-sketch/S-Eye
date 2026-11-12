# S-Eye implementation roadmap

Owner directive: 2026-11-12. Standing authorization covers ordinary engineering,
testing, commits and pull requests. Preserve independent algorithms and Stage 84.
Do not replace them with pretrained systems without explicit approval. Continue
substantive work while execution capacity and dependencies allow; save checkpoints.

Stage numbers are planning identifiers. Completion requires code, tests, measured
evidence and explicit limits; representative independent data is required for validation.

| Stages | Objective | Required evidence / current gate |
| --- | --- | --- |
| 85–89 | Multi-image generalization, grouped reproducible splits, duplicate/leakage checks; lighting/rotation/perspective/scale/background probes; class confusion and errors | Harness implemented; new reviewed photographs missing. Scale/background/perspective coverage remains incomplete |
| 90–99 | Adaptive thresholds, edges/contours, region merge/split, denoising, reconstructed boundaries, masks/boxes, overlaps and multiple objects | IoU and detection metrics on annotated instances, with baseline comparison |
| 100–109 | Modular geometric/color/texture/spatial features, similarity, prototypes, calibrated confidence, unknown rejection, candidate explanations | Per-class and unknown-class held-out evaluation |
| 110–119 | Dataset versions, independent initialization, reproducible training, saved/restored checkpoints, compatible preprocessing, learning curves, overfitting and model comparisons | Measured held-out improvement or documented non-improvement; no teacher labels presented as human truth |
| 120–129 | Persistent provenance-aware indexed memory, similar images, object history, retention, integrity, migrations, import/export and rollback | Retrieval quality and corruption recovery, preserving old formats |
| 130–139 | Inventories, spatial relations, grouping, scene similarity, grounded descriptions, changes/missing objects and uncertainty | Controlled and real-world scene validation |
| 140–149 | Prerecorded video frames/timestamps/sampling, motion, tracking, IDs, occlusion, persistence and summaries | Throughput, tracking errors and identity switches before live camera |
| 150–159 | Android ARM64/Termux, Linux and Windows resource/latency/batch/index/cache/storage optimization | Reproducible measurements and regression thresholds on actual tested hardware |
| 160–169 | Versioned Python/JSON APIs, S-Memory/S-Tools adapters, permissioned files/camera, requests, evidence-grounded visual Q&A, timeouts/errors | Independently testable integration client; no unrelated S changes |
| 170–179 | CLI, upload/analysis, overlays/reports, memory browser, annotation/experiment/config tools, installation/upgrades | A user completes workflows without editing source; UI only where justified |
| 180–189 | Input/path/resource limits, malformed files, permissions/privacy, atomic operations, migrations, crash/dependency/CI regression checks | All release-critical security/reliability checks pass |
| 190–199 | Full audit, integration/historical recognition/memory/video/performance/security/install tests, documentation/package/release preparation | All owner v1.0 gates fulfilled; otherwise remain experimental or release candidate |

This roadmap supplements existing instructions. It is not a declaration that
future features work. Preserve code, evidence and exact next steps before limits.
