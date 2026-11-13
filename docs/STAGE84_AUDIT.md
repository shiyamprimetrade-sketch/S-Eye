# Stage 84 repository audit

Baseline: `e92bb5594c193a50e01ae8e008a4020f7cc45f78` (`e92bb55`), Initial public release: S-Eye through Stage 84.

## Repository evidence

106 tracked files, including 99 Python files. Every baseline Python file parses
successfully under this host's Python 3.12. Original file hashes and top-level
function/class inventory are recorded in `benchmarks/stage84_inventory.json`.
This is a source audit, not proof that every historical script executes.

The repository has a single initial release checkpoint rather than 84 individual
stage commits. Stage claims come from source, README and checkpoint contents.
No pre-existing AGENTS.md, dependency lock or GitHub Actions workflow was present.
The supplied user engineering instructions apply to this continuation.

## Architecture through Stage 84

| Area | Existing implementation | Assessment |
| --- | --- | --- |
| Early experiments | eye.py, focus/attention, adaptive_mask, clusters, shapes, recognize variants | Small standalone experiments, many execute at import and expect local files |
| Geometry | geometry_v2_runner.py, geometry_v3_runner.py, stress/tolerance/borderline tests | Synthetic threshold/hull experiments; distinct from camera segmentation |
| Camera pipeline | local_contrast.py → group_shapes.py → filter_regions.py → classify_camera_v2.py | Pillow downsampling, dark local contrast, morphology, connected regions, convex hull and polygon simplification; no pretrained model |
| Main interface | s_eye.py | status, analyze, isolated; analyze selects camera photo by default |
| Source provenance | source_guard.py, session_manifest.py, archive_session.py | Hash guards and archived file inventories |
| Visual memory | visual_memory.py, upgrade_memory_v2.py, integrate_memory.py | Structured observations and schema upgrades; image-derived hypotheses |
| Isolation/index | isolated_analysis.py, build_memory_index.py, verify_memory_index.py | Per-run directories, source/output hashes and versioned run index |
| Concurrency/recovery | auto_memory.py, test_stage79.py, test_stage80.py | fcntl workflow locking, index rollback and historical checks dependent on local data |
| Dataset/evaluation | stage82_contact_sheet.py, stage83_labels.py, stage84_evaluate.py | Seven draft-labelled photo references; hardcoded target photo; provisional class presence only |
| Checkpoints | checkpoints/stage37.json, stage52.json, stage54.json, RESUME_STAGE85.txt | Historical assertions and fingerprints; retained unchanged |

## Reproduction on this host

`benchmarks/stage84_reproduction.json` retains exact stdout, stderr and exit codes
from disposable copies of the original scripts.

- Synthetic stress: 20/20 reported and confirmed by parsed output.
- Six-object synthetic geometry: six expected labels reproduced.
- Stage 84 evaluation: blocked by absent ground_truth_draft.json.
- Stage 79 concurrency: blocked by absent test photograph.
- Stage 80 recovery: blocked by absent memory index.

The repository deliberately ignores photos, stage82_dataset, isolated_runs,
sessions and visual-memory stores. The reported 48/48 archived fingerprints,
6 repeated photo analyses and seven inspected photos cannot be independently
replayed from this checkout. Historical claims are retained as historical.

## Findings and limits

1. Stage 84's normalization handles the word quadrilateral but omits Square-like
   and Rectangle-like. Stage 85 explicitly maps both to quadrilateral.
2. Stage 84 intersects sets but divides by list lengths; duplicates can depress
   its precision/recall proxies. Stage 85 uses set denominators consistently.
3. Six repeat runs of one photograph measure repeatability, not generalization.
4. Camera classification only recognizes broad geometric patterns. ≥5 simplified
   hull corners becomes Circle-like; this is not evidence of real object identity.
5. Fixed contrast threshold 18, minimum component area 100, morphology sizes and
   aspect-ratio rejection 0.45 imply sensitivity to dim/thin/small/elongated inputs.
6. Several historical experiments print failed cases while returning exit 0.
   New regression tests assert output values rather than trusting exit code alone.
7. Historical memory grouping/classification region IDs may require a separate
   audit when rejected regions alter numbering. Stage 85 evaluates class presence
   from classifier output and does not assert localization correctness.
8. This environment uses Python 3.12 and Pillow 13.0.0, not the historical Termux
   Python 3.13 runtime. CI targets both Python versions; remote results must be
   inspected separately before claiming they passed.

No existing algorithm, private memory, patch script or checkpoint was replaced.
