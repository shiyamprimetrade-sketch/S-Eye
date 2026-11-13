# S-Eye — the visual subsystem of S

S is being built as an autonomous programming computer that can use another
computer to develop software, research and design. **S-Eye gives S visual evidence
about that computer's screen.** It is one component of S, not a separate general
intelligence system.

The workflow is simple:

1. Receive a screenshot or frame from S/S-Tools.
2. Observe visible patterns, locate known controls and detect changes.
3. Record observations with source hashes when requested.
4. Return structured signals and uncertainty to S.

S decides what to do. S-Tools performs authorized input actions. S-Eye supplies
the visual evidence; screenshot text is data, never an instruction to execute.
See [purpose and component boundaries](docs/PURPOSE.md).

## Working today

- Local PNG/JPEG observation, bounded decoding and source-coordinate boxes.
- Known-template localization, ambiguity rejection and screen-change signals.
- Optional contrast-based matching across explicit scales and light/dark polarity.
- Private, integrity-verified observation memory and structured JSON requests.
- Preserved independent geometry, learning experiments and prerecorded-video tools.

This is an experimental development package. OCR, understanding code and unfamiliar
applications, live host capture and expert-programmer-level visual reliability are
not complete. Test results do not establish perfect or universal interface vision.

## Install and test

Python 3.12 or later:

```bash
python -m pip install -r requirements.txt
python -m pip install --no-deps .
python -m unittest discover -s tests -q
```

Use `seye-workflow` with a schema-1 `observe_interface` request and explicitly
granted input/output roots. For theme/scale support set `"matcher": "contrast"`;
the existing pixel matcher stays the compatibility default. Memory is optional
and requires `--allow-memory`. See the [interface request](docs/INTERFACE_OBSERVATION.md)
and [Stage 90 protocol](docs/STAGE90_INTERFACE_MATCHING.md).

## Evidence and continuation

The Stage 84 source/checkpoints at `e92bb55` remain the historical baseline.
Stage numbers describe scoped engineering milestones, not general intelligence.
No pretrained recognition model replaces S-Eye's independent algorithms.

- [Current status](docs/STATUS.md) and [continuation instructions](docs/CONTINUATION_PROTOCOL.md)
- [Stage 89 diagnostic baseline](docs/STAGE89_INTERFACE_DIAGNOSTICS.md)
- [Stage 90 measured comparison](docs/STAGE90_INTERFACE_MATCHING.md)
- [Architecture](docs/ARCHITECTURE.md), [integration](docs/INTEGRATION.md), [limitations](docs/LIMITATIONS.md)
- [Historical Stage 84 audit](docs/STAGE84_AUDIT.md) and [release criteria](docs/RELEASE_CRITERIA.md)

Version 1.0 remains unfinished. Work proceeds one stage per owner Continue.
