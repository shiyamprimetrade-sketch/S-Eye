"""From-scratch category prototypes, validation-derived rejection and JSON checkpoints.

This is independently fitted feature-based learning, not neural-network training.
Scores are distances/support indicators, never calibrated probabilities.
"""
import math
from seye.core.storage import atomic_json, checksum, read_json
from seye.recognition.features import FEATURE_VERSION, distance

UNKNOWN = '__unknown__'


def fit(training, validation):
    if not training or not validation:
        raise ValueError('Training and validation samples required')
    groups_train = {r['capture_group'] for r in training}
    if groups_train & {r['capture_group'] for r in validation}:
        raise ValueError('Training/validation capture leakage')
    labels = sorted({r['label'] for r in training})
    if UNKNOWN in labels or len(labels) < 2:
        raise ValueError('At least two known training classes; unknown cannot be trained as known')
    dimension = len(training[0]['features'])
    for row in training + validation:
        if len(row['features']) != dimension:
            raise ValueError('Feature dimension mismatch')
        distance(row['features'], row['features'])
    prototypes, radii, counts = {}, {}, {}
    for label in labels:
        samples = [r['features'] for r in training if r['label'] == label]
        counts[label] = len(samples)
        prototypes[label] = [sum(row[i] for row in samples) / len(samples) for i in range(dimension)]
        heldout = [r for r in validation if r['label'] == label]
        if not heldout:
            raise ValueError('Each known class requires validation samples')
        radii[label] = max(.015, max(distance(r['features'], prototypes[label]) for r in heldout) * 1.1)
    model = {'schema_version': 1, 'feature_version': FEATURE_VERSION, 'dimension': dimension,
             'method': 'independently_fitted_category_means', 'classes': labels,
             'prototypes': prototypes, 'radii': radii, 'training_counts': counts,
             'probability_calibrated': False, 'pretrained_weights_used': False}
    validate_model(model)
    return model


def validate_model(model):
    if model.get('method') == 'independent_linear_softmax_sgd':
        from seye.learning.linear import validate
        return validate(model)
    if model.get('schema_version') != 1 or model.get('feature_version') != FEATURE_VERSION:
        raise ValueError('Incompatible model/preprocessing version')
    if type(model.get('dimension')) is not int or not 1 <= model['dimension'] <= 4096:
        raise ValueError('Invalid model dimension')
    labels = model.get('classes')
    if not isinstance(labels, list) or not 2 <= len(labels) <= 1000 or any(not isinstance(s, str) or not s or s == UNKNOWN for s in labels) or len(set(labels)) != len(labels):
        raise ValueError('Invalid known classes')
    if set(model['prototypes']) != set(labels) or set(model['radii']) != set(labels):
        raise ValueError('Model class inventories differ')
    for label in labels:
        vector = model['prototypes'][label]
        if len(vector) != model['dimension']:
            raise ValueError('Invalid prototype dimension')
        distance(vector, vector)
        radius = model['radii'][label]
        if type(radius) not in (int, float) or not math.isfinite(radius) or radius <= 0:
            raise ValueError('Invalid rejection radius')
    return model


def predict(model, features):
    if model.get('method') == 'independent_linear_softmax_sgd':
        from seye.learning.linear import predict as linear_predict
        return linear_predict(model, features)
    validate_model(model)
    if len(features) != model['dimension']:
        raise ValueError('Inference preprocessing dimension mismatch')
    candidates = sorted(({'label': label, 'distance': distance(features, model['prototypes'][label]),
                          'rejection_radius': model['radii'][label]} for label in model['classes']),
                        key=lambda row: (row['distance'], row['label']))
    first = candidates[0]
    accepted = first['distance'] <= first['rejection_radius']
    return {'label': first['label'] if accepted else UNKNOWN, 'accepted': accepted,
            'candidates': candidates, 'confidence_probability': None,
            'explanation': 'Nearest fitted descriptor mean within validation-derived radius' if accepted else
                           'No known category is within its validation-derived descriptor radius'}


def save_model(path, model):
    validate_model(model)
    return atomic_json(path, {'model': model, 'sha256': checksum(model)})


def load_model(path):
    envelope = read_json(path)
    if checksum(envelope['model']) != envelope.get('sha256'):
        raise ValueError('Model checkpoint integrity mismatch')
    return validate_model(envelope['model'])


def evaluate(model, samples):
    confusion = {}
    results = []
    for row in samples:
        output = predict(model, row['features'])
        pair = (row['label'], output['label'])
        confusion[pair] = confusion.get(pair, 0) + 1
        results.append({'id': row['id'], 'expected': row['label'], 'prediction': output,
                        'source_kind': row.get('source_kind', 'unspecified'),
                        'annotation_status': row.get('annotation_status', 'unspecified')})
    known = [r for r in results if r['expected'] != UNKNOWN]
    unknown = [r for r in results if r['expected'] == UNKNOWN]
    partitions = []
    for kind, annotation in sorted({(r['source_kind'], r['annotation_status']) for r in results}):
        subset = [r for r in results if r['source_kind'] == kind and r['annotation_status'] == annotation]
        partitions.append({'source_kind': kind, 'annotation_status': annotation, 'samples': len(subset),
                           'correct': sum(r['expected'] == r['prediction']['label'] for r in subset)})
    return {'partitions': partitions, 'samples': len(results), 'correct': sum(r['expected'] == r['prediction']['label'] for r in results),
            'known_samples': len(known), 'known_correct': sum(r['expected'] == r['prediction']['label'] for r in known),
            'unknown_samples': len(unknown), 'unknown_rejected': sum(not r['prediction']['accepted'] for r in unknown),
            'confusion': [{'expected': a, 'predicted': b, 'count': count} for (a, b), count in sorted(confusion.items())],
            'results': results}
