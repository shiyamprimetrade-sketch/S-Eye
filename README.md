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
