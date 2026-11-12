"""Independent monotonic validation-score calibration; no accuracy guarantees."""
import math


def fit(scores, correct):
    if not scores or len(scores) != len(correct):
        raise ValueError('Aligned nonempty validation scores/outcomes required')
    if any(type(s) not in (int, float) or not math.isfinite(s) or not 0 <= s <= 1 for s in scores):
        raise ValueError('Scores must be finite in [0,1]')
    if any(type(y) is not bool for y in correct):
        raise ValueError('Correctness outcomes must be booleans')
    grouped = {}
    for score, outcome in zip(scores, correct):
        total, count = grouped.get(score, (0, 0)); grouped[score] = (total + outcome, count + 1)
    blocks = []
    for score, (total, count) in sorted(grouped.items()):
        blocks.append({'lower': score, 'upper': score, 'total': total, 'count': count})
        while len(blocks) > 1 and blocks[-2]['total']/blocks[-2]['count'] > blocks[-1]['total']/blocks[-1]['count']:
            right = blocks.pop(); left = blocks.pop()
            blocks.append({'lower': left['lower'], 'upper': right['upper'], 'total': left['total']+right['total'], 'count': left['count']+right['count']})
    return {'schema_version': 1, 'method': 'validation_isotonic_frequency', 'samples': len(scores),
            'blocks': blocks, 'representative_validation': False}


def estimate(model, score):
    if type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError('Finite score in [0,1] required')
    if model.get('schema_version') != 1 or not model.get('blocks'):
        raise ValueError('Calibration model required')
    block = next((b for b in model['blocks'] if score <= b['upper']), model['blocks'][-1])
    return {'validation_support_estimate': block['total']/block['count'], 'support_samples': block['count'],
            'confidence_probability': None, 'scope': 'empirical validation frequency; not representative truth probability'}


def brier(scores, correct):
    fit(scores, correct)  # Shared strict input validation.
    return sum((s-int(y))**2 for s,y in zip(scores,correct))/len(scores)
