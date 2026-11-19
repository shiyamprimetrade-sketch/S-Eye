# Repository map

| Directory | Contents |
| --- | --- |
| **src/seye/** | Installable Python package. **api/** contains entry points and **integration/** contains request permissions and adapters. Image, recognition, memory, scene, and video modules do the work. |
| **android/** | Native Android manifest, Java sources, APK build script, and verification helpers. |
| **tests/** | Desktop unit tests, integration tests, and historical regressions. |
| **scripts/** | Reproducible benchmarks, audits, and installed-package smoke checks. |
| **benchmarks/** | Historical evidence and current benchmark results. |
| **datasets/** and **experiments/** | Dataset manifests and experimental protocols. |
| **checkpoints/** | Preserved model and historical checkpoint files. |
| **docs/** and **tasks/** | Guides, contracts, release criteria, and the 86–199 stage registry. |
| **legacy/stage84/** | Historical scripts and early evaluation tools in their original flat layout. |
| **.github/workflows/** | Python verification, Android APK builds, and emulator verification. |

The root keeps project configuration, documentation entry points, and the
**analyze_image.py** compatibility launcher. The archive keeps sibling scripts
together so their filename references still work. For scripts that write output,
run from a scratch copy:

    archive="$(mktemp -d)"
    cp -R legacy/stage84/. "$archive/"
    (cd "$archive" && python stress_test.py)

The Stage 84 audit checks the original inventory against relocated bytes.
The early dataset and generalization tools had their import and fingerprint
paths adjusted to reach the package source. Run from the checkout:

    python legacy/stage84/stage85_fixture.py /tmp/new-seye-fixtures
    python legacy/stage84/generalization.py --manifest /tmp/new-seye-fixtures/manifest.json --output /tmp/new-seye-result.json

Historical documents and ledger entries record paths at their checkpoint
commits. For an old root-level command, look in **legacy/stage84/**.
