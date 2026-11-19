# S-Eye

S-Eye gives **S**, the programming computer, visual evidence. It observes
images, locates supported patterns, compares screenshots, and returns structured
results for S to interpret.

| Area | Where to start |
| --- | --- |
| Android | [Install, take photos, and export observations](android/README.md) |
| Desktop | [Local workflow guide](docs/LOCAL_WORKFLOWS.md) |
| Integration | [S interface](docs/INTEGRATION.md) and [Android JSON contract](docs/ANDROID_INTEGRATION.md) |
| Evidence | [Current status](docs/STATUS.md), [benchmarks](docs/BENCHMARKS.md), and [release criteria](docs/RELEASE_CRITERIA.md) |
| Repository | [Directory map and legacy instructions](docs/REPOSITORY_MAP.md) |

## Desktop quick start

With Python 3.12 or later:

    python -m pip install -r requirements.txt
    python -m pip install --no-deps .
    seye-local doctor
    python -m unittest discover -s tests -q

Some video workflows use FFmpeg. Run **seye-workflow --describe-contract** to
list the JSON actions or start with the [interface observer](docs/INTERFACE_OBSERVATION.md).
The desktop and Android packages remain experimental. Representative recognition,
live host capture, and deployment in the parent S application remain open.
See the [project purpose](docs/PURPOSE.md) and [Stage 199 checkpoint](docs/STAGES_191_199.md).
