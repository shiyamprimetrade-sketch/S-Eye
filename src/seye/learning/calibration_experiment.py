"""Fit validation predictions only; retain an explicitly exploratory test evaluation."""
from seye.learning.calibration import fit, estimate, brier
from seye.core.storage import checksum


def evidence(rows):
    ids, scores, outcomes = set(), [], []
    for row in rows:
        if row['id'] in ids:
            raise ValueError('Duplicate prediction identity')
        ids.add(row['id'])
        candidate = row['prediction']['candidates'][0]
        scores.append(candidate['raw_softmax_score'])
        outcomes.append(candidate['label'] == row['expected'])
    return ids, scores, outcomes


def experiment(validation, testing):
    val_ids, val_scores, val_truth = evidence(validation)
    test_ids, test_scores, test_truth = evidence(testing)
    if val_ids & test_ids:
        raise ValueError('Validation/test prediction identity leakage')
    model = fit(val_scores, val_truth)
    calibrated = [estimate(model, score)['validation_support_estimate'] for score in test_scores]
    return {'schema_version': 1, 'calibration_model': model,
            'fit_partition': 'validation_only', 'validation_predictions_sha256': checksum(validation),
            'test_predictions_sha256': checksum(testing), 'validation_samples': len(validation),
            'test_samples': len(testing), 'raw_test_brier': brier(test_scores, test_truth),
            'calibrated_test_brier': brier(calibrated, test_truth),
            'recognition_labels_changed': False, 'representative_validation': False,
            'limitations': ['Previously inspected generated test; exploratory only, not a new locked test.',
                            'Calibrating correctness estimates does not fix category/unknown mistakes.']}
