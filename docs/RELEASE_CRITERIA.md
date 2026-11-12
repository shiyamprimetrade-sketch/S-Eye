# Version 1.0 release criteria

Status: **not met**. The project remains experimental; never declare completion
from a stage number, successful script execution or synthetic-only accuracy.

| Gate | Required proof | Current status |
| --- | --- | --- |
| Image analysis | Installable ingestion and evidence-grounded reports | Baseline/harness implemented and tested; install release pending |
| Multi-object detection/localization | Documented supported conditions and representative box/mask evaluation | Pending |
| Recognition/rejection | Independent category evidence and unknown inputs rejected | Geometry-only; broader recognition/rejection pending |
| Visual memory | Persistent retrieval, provenance, integrity and failure recovery | Historical implementation; new representative verification pending |
| Scenes | Supported change/similarity workflows tested on scenes | Historical experiments; validation pending |
| Video | Prerecorded tracking and errors/throughput measured | Pending |
| S integration | Versioned contract and end-to-end client | Pending |
| Independent learning | Reproducible initialized training, restored checkpoints, compatible preprocessing, held-out evaluation | Pending |
| Reliability | Automated tests, backward compatibility/migrations, crash recovery and no known release-blocking security issue | Partial tests; full hardening pending |
| Deployment | Installation verified on at least one supported environment, usable interface, examples and versioned artifacts | Pending |
| Evidence | Reproducible datasets/protocols, benchmark results, traceable GitHub work and honest supported scope | Infrastructure implemented; representative validation pending |

If a mandatory gate is missing, keep an experimental/release-candidate status.
Reducing mandatory release scope requires owner approval. Ordinary engineering,
testing and publication of development branches do not need repeated approval.
