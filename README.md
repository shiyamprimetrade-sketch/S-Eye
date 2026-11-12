# S-Eye

S-Eye is an experimental computer vision and
visual memory subsystem developed for the S project.

## Capabilities

- Camera image processing
- Local contrast segmentation
- Geometric shape classification
- Visual change detection
- Visual memory and indexing
- SHA-256 artifact verification
- Isolated analysis runs
- Concurrent workflow coordination
- Failure recovery testing
- Reproducible analysis checkpoints

## Development status

Latest completed milestone: Stage 84

Verified historical results:
- 20/20 synthetic shape stress tests
- 6/6 additional synthetic geometry tests
- 48/48 archived fingerprints verified
- Concurrent workflow test passed
- Failure recovery test passed
- 6 repeated analyses of one photograph
  matched 3 provisional shape categories

These results do not establish general object
recognition accuracy.

Next milestone:
Stage 85 — Generalization across new photographs.

## Environment

Python 3.13
Pillow
Android / Termux

## Development policy

Preserve existing working components.
Verify changes before accepting them.
Separate measured results from experimental claims.

## Stage 85 engineering continuation

The Stage 85 evaluation harness is implemented. Photographic generalization
remains pending new captures and reviewed labels. Existing camera algorithms
and historical checkpoints are preserved.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python stage85_fixture.py /tmp/s-eye-fixture --stress
python generalization.py --manifest /tmp/s-eye-fixture/manifest.json --output /tmp/s-eye-report.json
```

See [development status](DEVELOPMENT_STATUS.md), the
[Stage 84 audit](docs/STAGE84_AUDIT.md) and
[Stage 85 capture/evaluation protocol](docs/STAGE85_PROTOCOL.md).
Generated fixtures are synthetic; they do not establish real-photo accuracy.

## Structured localization (experimental)

```bash
python -m pip install .
seye --image /path/to/photo.jpg --output-dir /path/to/new-analysis
```

Returns geometric boxes, masks, an overlay and JSON. The default preserves the
legacy baseline; `--mode adaptive` enables an independent experimental contrast
rule. See [localization and installation](docs/LOCALIZATION.md),
[grouped datasets](docs/DATASETS.md), and [release gates](docs/RELEASE_CRITERIA.md).
Broader recognition, learned confidence, video tracking and full S integration
remain incomplete. This is a development package, not S-Eye v1.0.

## Independent learning, memory, scenes and prerecorded video

New experimental modules support prototype fitting and seeded SGD linear training
from scratch over fixed S-Eye descriptors; checksum-verified model checkpoints;
private local observation retrieval/export/import; geometric scene comparison;
and optional FFmpeg video-frame decoding with an independent box tracker.

```bash
python scripts/benchmark_independent_system.py --output /tmp/new-system-experiment.json
seye-workflow --request /path/to/request.json --output /path/to/new-response.json --read-root /path/to --write-root /path/to
```

See [learning and measured failures](docs/LEARNING.md),
[instance annotations](docs/INSTANCE_ANNOTATIONS.md),
[memory/scenes/video](docs/MEMORY_SCENES_VIDEO.md), and
[integration requests and permissions](docs/INTEGRATION.md).
The experiment is generated-data research; the current learned classifiers have
not improved total test correctness over fixed geometry. Broader photographic
recognition and final v1.0 remain unvalidated.

Every roadmap number 86–199 is tracked in
[tasks/stages_086_199.json](tasks/stages_086_199.json), with explicit open requirements.
[Release readiness](benchmarks/release_readiness.json) remains false.
