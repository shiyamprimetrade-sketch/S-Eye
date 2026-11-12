"""Independently initialized linear softmax classifier trained with explicit SGD.

Fixed S-Eye descriptors are inputs; this is not learned representation/deep vision.
Raw softmax scores are uncalibrated and never advertised as probabilities of truth.
"""
import math
import random
from seye.recognition.features import FEATURE_VERSION, distance


def scores(model, features):
    if len(features) != model['dimension']:
        raise ValueError('Linear classifier feature dimension mismatch')
    distance(features, features)
    logits = [sum(w*x for w,x in zip(weights, features)) + bias for weights,bias in zip(model['weights'], model['bias'])]
    peak = max(logits); exponentials = [math.exp(value - peak) for value in logits]; total = sum(exponentials)
    return [value / total for value in exponentials]


def validate(model):
    if model.get('schema_version') != 1 or model.get('feature_version') != FEATURE_VERSION or model.get('method') != 'independent_linear_softmax_sgd':
        raise ValueError('Incompatible linear model version')
    labels = model.get('classes', [])
    if not isinstance(labels, list) or not 2 <= len(labels) <= 64 or any(not isinstance(s, str) or not s or s == '__unknown__' for s in labels) or len(set(labels)) != len(labels):
        raise ValueError('Invalid linear class inventory')
    if type(model.get('dimension')) is not int or not 1 <= model['dimension'] <= 4096:
        raise ValueError('Invalid linear model dimension')
    if len(model['weights']) != len(labels) or len(model['bias']) != len(labels):
        raise ValueError('Invalid linear parameter inventory')
    for weights in model['weights']:
        if len(weights) != model['dimension']:
            raise ValueError('Invalid linear weight dimensions')
        distance(weights, weights)
    distance(model['bias'], model['bias'])
    if not 0 <= model['rejection_threshold'] <= 1:
        raise ValueError('Invalid rejection threshold')
    return model


def predict(model, features):
    validate(model)
    values = scores(model, features)
    candidates = sorted(({'label': label, 'raw_softmax_score': score} for label, score in zip(model['classes'], values)),
                        key=lambda r: (-r['raw_softmax_score'], r['label']))
    accepted = candidates[0]['raw_softmax_score'] >= model['rejection_threshold']
    return {'label': candidates[0]['label'] if accepted else '__unknown__', 'accepted': accepted,
            'candidates': candidates, 'confidence_probability': None,
            'explanation': 'Independent SGD linear-class score above validation-derived threshold' if accepted else
                           'Raw linear-class score below validation-derived rejection threshold'}


def fit(training, validation, epochs=120, seed=91, learning_rate=.1):
    if type(epochs) is not int or not 1 <= epochs <= 1000 or type(seed) is not int or type(learning_rate) not in (int, float) or not math.isfinite(learning_rate) or not 0 < learning_rate <= 1:
        raise ValueError('Invalid independent SGD configuration')
    if not training or not validation or {r['capture_group'] for r in training} & {r['capture_group'] for r in validation}:
        raise ValueError('Training/validation data required without capture leakage')
    labels = sorted({r['label'] for r in training})
    if '__unknown__' in labels or len(labels) < 2:
        raise ValueError('At least two known training classes required')
    if any(not any(r['label'] == label for r in validation) for label in labels):
        raise ValueError('Validation examples for every known class required')
    dimension = len(training[0]['features']); rng = random.Random(seed)
    model = {'schema_version': 1, 'feature_version': FEATURE_VERSION, 'method': 'independent_linear_softmax_sgd',
             'classes': labels, 'dimension': dimension,
             'weights': [[rng.uniform(-.01, .01) for _ in range(dimension)] for _ in labels], 'bias': [0.] * len(labels),
             'rejection_threshold': 0., 'seed': seed, 'epochs': epochs, 'learning_rate': learning_rate,
             'pretrained_weights_used': False, 'probability_calibrated': False}
    for row in training + validation:
        if len(row['features']) != dimension:
            raise ValueError('Training descriptor dimension mismatch')
        distance(row['features'], row['features'])
    validate(model)
    order = list(range(len(training))); history = []
    for epoch in range(epochs):
        rng.shuffle(order)
        for index in order:
            row = training[index]; values = scores(model, row['features']); target = labels.index(row['label'])
            for c in range(len(labels)):
                gradient = values[c] - int(c == target)
                model['bias'][c] -= learning_rate * gradient
                for feature in range(dimension):
                    model['weights'][c][feature] -= learning_rate * gradient * row['features'][feature]
        if epoch == 0 or (epoch + 1) % 10 == 0 or epoch == epochs - 1:
            metrics = {}
            for name, rows in (('training', training), ('validation', [r for r in validation if r['label'] in labels])):
                loss = sum(-math.log(max(1e-15, scores(model, r['features'])[labels.index(r['label'])])) for r in rows) / len(rows)
                correct = sum(labels[max(range(len(labels)), key=lambda c: scores(model, r['features'])[c])] == r['label'] for r in rows)
                metrics[name] = {'cross_entropy': loss, 'correct_before_rejection': correct, 'samples': len(rows)}
            history.append({'epoch': epoch + 1, **metrics})
    known_scores = [max(scores(model, r['features'])) for r in validation if r['label'] in labels]
    model['rejection_threshold'] = max(.5, min(known_scores) * .9)
    model['training_history'] = history
    return validate(model)
