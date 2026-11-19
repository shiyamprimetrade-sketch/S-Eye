# Stage 89 — automatic interface-condition evaluation

Engineering acceptance: complete. Representative application validation: absent.
The owner's interface-observation priority and no-human-review requirement are
preserved. This stage measures the fixed Stage 88 matcher; it does not replace it
or claim to resolve its theme/scale failures.

## Reproducible experiment

```bash
python scripts/benchmark_stage89.py --output /absolute/new/stage89.json
python -m unittest discover -s tests -q
```

The benchmark renders three independent glyph designs (run/stop/menu), two themes,
three scales (1, 1.5, 2), and four states (single, absent, duplicate, half occluded):
72 cases. Unchanged-frame, four-pixel cursor and viewport-resize controls bring the
total to 75. The three glyphs share rendering primitives: this is a generated test
matrix, not a representative set of independently developed applications.

Ground-truth boxes, supported-target counts and changed-pixel counts are emitted by
the renderer before predictions. Metadata labels represent the test contract;
occluded controls are deliberately unsupported and should be rejected, not located.
Expected pixel counts come from construction areas, and tests independently check
them against rendered bytes. There are no human review flags or guessed real-world
annotations. Screenshot/template/previous-frame SHA-256 identities and an aggregate
fixture identity are included. Two complete benchmark runs produced identical JSON
on this host. Timing is excluded from the identity/reproducibility experiment.

Every family uses one native-size dark template. Theme and scale variation are
applied to scene controls, not silently supplied as additional reference templates.
No training, threshold search or test-data tuning is performed. Matcher stride is
four pixels and similarity threshold is 1, an exact-pixel diagnostic setting rather
than the API's default 0.97. Results do not establish behavior at other thresholds.
The full matrix is an evaluation set, not a train/validation/test learning split.

## Recorded results

| Measurement | Result |
| --- | ---: |
| Executions completed | 75 / 75 |
| Expected status matches | 45 / 75 |
| Unique controls localized at IoU ≥ 0.5 | 3 / 18 |
| Missed unique controls | 15 / 18 |
| False accepted candidates | 0 |
| Absent/unsupported rejection cases | 39 |
| Duplicate-control cases labeled ambiguous | 3 / 18 |
| Unsafe single selections on duplicate controls | 0 / 18 |
| Exact change signal and pixel-count oracle matches | 75 / 75 |

The remaining 15 duplicate cases return not-found, not successful ambiguity
recognition. Only native-size dark controls localize; light-theme controls and all
scaled unique controls are missed. Zero false accepts on these sparse generated
negatives is not proof of safe behavior on unfamiliar real interfaces.

The cursor control changes four pixels and emits `pixels_changed`, but produces
no tile-region box because the change is below the active-tile fraction threshold.
A signal and a localized region are separate outputs. Viewport resizing correctly
abstains from pixel comparison. No text content or programming meaning is inferred.

## Report contract and verification

`src/seye/interface/evaluation.py` accounts for every requested case, including
execution errors. Status confusion matrices include an execution-error column.
It reports unique-target IoU true/false positives and false negatives, unsafe
single-choice counts, condition breakdowns and error examples. Incorrect boxes
count as both a false positive and a missed target even when status strings match.
Failures cannot disappear from the requested-case denominator or count as completed
change checks. Duplicate IDs, malformed or missing oracles, degenerate boxes and
candidates attached to abstention outputs are rejected.

112 local tests pass. Six new tests cover wrong-location accounting, false accepts,
ambiguity safety, execution errors, invalid oracles, deterministic fixture identity,
analytic pixel counts and the complete negative-result benchmark. CI runs the new
benchmark and uploads its report; benchmark exit success means execution completed,
not that recognition succeeded. Regression tests preserve the current measured
failure pattern and should be deliberately revised with evidence when improved.

## Next stage

On the next Continue, Stage 90 should evaluate independent contrast/edge processing
and bounded multiscale matching against this frozen baseline. Preserve the fixed
matcher as a comparator. Use additional held-out generated designs/positions and
negative cases before selecting parameters; include ambiguity and resource-budget
checks. Keep OCR, code comprehension, OS capture/actions and representative real
application validation explicitly unfinished. Do not require human review to
continue ordinary engineering, and do not declare expert programmer equivalence.
