# Unlabelled real-input testing

`seye.core.probes` and `scripts/probe_images.py` evaluate bounded local image
execution and repeatability without fabricating annotation-based accuracy.
They accept photographs and screenshots as separate source kinds. No screenshot
text is executed, and no OCR/hand/furniture recognition is implied by geometric labels.

A schema-1 probe manifest resides beside its image files:

```json
{
  "schema_version": 1,
  "annotation_status": "unlabelled",
  "images": [
    {"id": "capture-01", "path": "capture-01.jpg", "sha256": "ACTUAL_SHA256", "source_kind": "photograph"},
    {"id": "screen-01", "path": "screen-01.jpg", "sha256": "ACTUAL_SHA256", "source_kind": "screenshot"}
  ]
}
```

The strings `ACTUAL_SHA256` are placeholders, not experimental evidence.
Run from a checkout:

```bash
python scripts/probe_images.py --manifest /path/to/manifest.json --output /path/to/new-report.json --overlays /path/to/new-overlay-directory
```

Default conditions: original bytes twice, simulated brightness ×0.55 once and
simulated 15-degree image rotation once, each through baseline and adaptive modes.
This is eight runs per input, not eight independent camera captures. All sources
are validated before inference. A failed run remains counted and is reported;
repeatability is null for failures or a single repetition. Existing output paths
are preserved. Overlay names use numeric indices rather than untrusted image IDs.

The report explicitly leaves recognition/localization accuracy null. To score
recognition or boxes, use a separate reviewed-annotation evaluation protocol;
this probe rejects ground-truth/confirmation fields. Predictions and source/mask
hashes are measurements of software output, not labels proving correctness.

## Uploaded-input experiment — 2026-11-12

Five user-supplied files: one hand/interior camera photograph (2652) and four
screenshots (2647, 2561, 2526, 2524), classified by assistant visual inspection.
This source classification is not a recognition result from S-Eye. No independent
semantic object or box ground truth was supplied or confirmed. These images do
not provide the three new photographs of the same geometric shapes needed for
the original Stage 85 capture protocol.

`benchmarks/uploaded_input_probe.json` records all 40 executions and original
repeatability. Uploaded image pixels and overlays are kept outside git; only code,
hashes and numeric/structured geometric outputs are published. Reproduction of
this exact experiment requires the five original byte-identical uploaded images;
the reusable code and generated unit controls can run without them.

The current geometric engine proposes circular/polygonal regions even in hands,
furniture textures, text and UI elements. Proposal count is not object count or
semantic recognition success. Adaptive producing fewer proposals is not evidence
that it is more accurate. Reviewed representative annotations and a classifier
with supported semantic categories remain required.
