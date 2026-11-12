"""Multi-label class-presence diagnostics, not instance/localization accuracy."""
from collections import defaultdict

LABELS = ('circle', 'quadrilateral', 'triangle', 'unknown')


def diagnostics(results):
    groups = defaultdict(list)
    for row in results:
        key = (row['source_kind'], row['human_confirmed'], row.get('split', 'unsplit'), row['variant'])
        groups[key].append(row)
    summaries = []
    errors = []
    for key, rows in sorted(groups.items()):
        matrices = {label: {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0} for label in LABELS}
        for row in rows:
            expected = set(row['expected_classes'])
            if not row['pipeline_success']:
                errors.append({'id': row['id'], 'variant': row['variant'], 'split': row.get('split', 'unsplit'),
                               'kind': 'pipeline_error', 'error': row['error']})
                continue  # Report failures separately, never fabricate classifier output.
            predicted = set(row['prediction']['classes'])
            for label in LABELS:
                outcome = ('tp' if label in expected else 'fp') if label in predicted else ('fn' if label in expected else 'tn')
                matrices[label][outcome] += 1
            missing, extra = sorted(expected - predicted), sorted(predicted - expected)
            if missing or extra:
                errors.append({'id': row['id'], 'variant': row['variant'], 'split': row.get('split', 'unsplit'),
                               'kind': 'class_mismatch', 'false_negative_classes': missing,
                               'false_positive_classes': extra})
        for label, counts in matrices.items():
            tp, fp, fn = counts['tp'], counts['fp'], counts['fn']
            counts['precision'] = tp / (tp + fp) if tp + fp else None
            counts['recall'] = tp / (tp + fn) if tp + fn else None
        summaries.append({'source_kind': key[0], 'human_confirmed': key[1], 'split': key[2],
                          'variant': key[3], 'attempted_cases': len(rows),
                          'pipeline_failures': sum(not r['pipeline_success'] for r in rows),
                          'exact_matches': sum(r.get('metrics', {}).get('exact_match', False) for r in rows),
                          'binary_confusion_by_class': matrices})
    return {'metric_type': 'multi_label_class_presence',
            'confusion_matrix_scope': 'Successfully executed cases only; pipeline failures excluded and separately counted.',
            'summaries': summaries, 'error_examples': errors}
