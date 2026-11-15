# Local workflows · S-Eye 0.1.0.dev180

These tools work on files you explicitly select. They do not capture a camera,
operate another computer, publish data or silently replace existing outputs.
Generated regions and supplied prototype labels remain experimental evidence.

## Installation and upgrades

Python 3.12 or newer and the pinned Pillow dependency are required. From a checkout
of the intended S-Eye revision, use a dedicated environment and install that exact
revision. Record `git rev-parse HEAD` alongside results; package/API versions alone
do not identify all source changes.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
seye-local --version
seye-local doctor --require-installed --self-test
```

For an upgrade, preserve your existing workspaces, memories, models and profiles.
Install the reviewed new checkout/wheel into a fresh environment first, run the
doctor/self-test, then compare source-bound reports. No command below upgrades an
existing data/schema file in place. Config migration writes an exclusive new file.
The development version is `0.1.0.dev180`; this is not a version 1.0 release.
FFmpeg is optional for image-only local workflows and required by video features.
Node is used only by the development editor-logic check, not by the installed CLI.

## Capture snapshots and view evidence

Replace `/absolute/work` with your own directory. Place your captured images below
that directory. Quote paths containing spaces. All new output directories must be
unused; use a different name for the next run.

```bash
seye-local --root /absolute/work ingest \
  --images /absolute/work/screen.png --source-kind screenshot \
  --output /absolute/work/capture-run
seye-local --root /absolute/work overlays \
  --workspace /absolute/work/capture-run --output /absolute/work/overlay-run
seye-local --root /absolute/work report \
  --workspace /absolute/work/capture-run --output /absolute/work/report-run
```

Open `overlay-run/image-0001.png` or `report-run/report.html` using a browser/image
viewer that is independently permitted to open your local files. The report is
self-contained and has no network fetches. Amber boxes are geometric hypotheses,
not proven objects, controls or click targets. Without `--model`, recognition is
explicitly `not_requested`. With `--model /absolute/work/model.json`, only a
supported schema-bound packet prototype checkpoint is used. Its labels are supplied
training categories, not semantic truth; no calibrated confidence is invented.

Input snapshots preserve source bytes and EXIF-oriented coordinates. Copied inputs
are hash-checked on use. Every bundle has a checksummed `manifest.json` completion
marker written last. A missing/invalid marker means incomplete output. Publication
is exclusive, not an atomic directory rename/power-loss transaction. Abrupt process
termination can leave a private staging/partial directory; choose a fresh output
name after inspecting such an interrupted run. No automatic cleanup deletes user
workspaces, and existing output directories/files are never overwritten.

## Draft annotations

```bash
seye-local --root /absolute/work annotate \
  --workspace /absolute/work/capture-run --output /absolute/work/editor-run
seye-local --root /absolute/work validate-draft \
  --workspace /absolute/work/capture-run --draft /absolute/work/editor-run/draft.json
```

`editor-run/annotate.html` is a standalone geometric box editor. Choose an image
and class, drag a box, undo the last box or download JSON. Preview coordinates map
to the original EXIF-oriented source grid; previews can be downscaled. Supply a
previous downloaded draft with `annotate --draft FILE` to continue editing it.
The source identity/inventory is checked before an existing draft is loaded.

Drafts remain `template_unscored=true`, `annotation_status=draft` and
`annotation_origin=caller_drawn`. An empty draft does not assert a negative image.
Source kinds/capture groups are caller declarations, not authenticated provenance.
The editor does not mark human review or generator truth, train a model or convert
its own hypotheses into validation labels. This draft format is deliberately
separate from the scored annotation manifest; draft validation checks identities,
boxes and bounds, not correctness of the labels.

Real-browser rendering/usability has **not** been verified in this environment.
The attempted Chromium launch failed at a prohibited socket, and the shared
browser refused local-file URLs. No browser-policy workaround was attempted.
Node test doubles verify drawing/coordinate/download/undo logic in three scaling
cases; that is not a browser renderer, mobile-device test or human usability study.

## Read-only memory pages and source-matched comparisons

```bash
seye-local --root /absolute/work memory \
  --memory /absolute/work/eye.sqlite3 --limit 20 \
  --output /absolute/work/memory-page-1
seye-local --root /absolute/work compare \
  --left /absolute/work/report-run/report.json \
  --right /absolute/work/second-report/report.json \
  --output /absolute/work/comparison-run
```

Open `memory-page-1/memory.html`. The JSON page exposes `next_after` and
`inventory_sha256`; pass them as `--after` and `--expected-snapshot` for the next
page. If memory changes, start a fresh view. Reads verify content and preserve
observation records; stored text/labels are displayed as escaped untrusted data.
No thumbnails are invented for historical records whose pixels are unavailable.

Comparison requires the same complete image identities by default. Explicit
`--allow-partial` retains missing/source-incomparable slots in the denominator.
Region-count or decision changes are not accuracy improvements without independent
labels. `accuracy_change` stays null. Model, schema, capture or source changes are
confounds; this tool does not turn an unlabeled comparison into a benchmark win.

## Configuration

```bash
seye-local --root /absolute/work config-init --output /absolute/work/read-only.json
seye-local --root /absolute/work config-inspect --path /absolute/work/read-only.json
seye-local --root /absolute/work config-migrate \
  --source /absolute/work/old.json --output /absolute/work/migrated.json
```

New profiles default to read access under the chosen root and no write/memory/
training/video capability. `config-init --allow-write` and `--allow-memory` are
explicit choices. Inspection/migration does not apply a profile. Version-0 to
version-1 export preserves normalized grants and never overwrites the source.
Use an inspected profile with the existing `seye-workflow --config FILE` interface
when you explicitly want those grants applied to a request workflow.

## Limits and error behavior

- Inputs: 1..32 explicit images, 32 MiB / 4 million pixels per image; a workspace
  caps accepted source bytes at 64 MiB and total decoded pixels at 32 million.
- Existing outputs, dangling output symlinks, path escapes, malformed sources,
  mismatched source identities and invalid completion markers are refused.
- Overlays: at most 128 source-grid boxes. Reports: 8 MiB JSON / 16 MiB HTML;
  supplied training labels are bounded. Failed prototype inference is reported as
  failure, not a fabricated unknown-object prediction.
- Memory browser: at most 10000 observations / 256 MiB database, pages of 1..100
  records, at most 8 MiB output per JSON page. SQLite may manage its own sidecars;
  read-only refers to observation content and no explicit mutation/compaction.
- Editor: at most 128 boxes per image; 2 MiB draft / 16 MiB standalone editor.
  Geometric labels are caller assertions; no review is authenticated.
- JSON files: bounded UTF-8 with optional UTF-8 BOM, no duplicate keys/nonfinite
  values/unpaired surrogates, post-parse depth <=64 and at most one million nodes.
  Encoded/post-parse limits are not a hard native-RSS guarantee.
- CLI: exit 0 on success, 1 for a required-installation check failure, 2 for invalid
  setup/input/operation. `doctor` does not download/install/upgrade software.

All measurements are generated engineering controls. Actual Android hardware,
representative application recognition, live camera, main-S deployment, native
sandbox/crash campaigns and version 1.0 release gates remain open.
