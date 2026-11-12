"""Versioned classification data with full split leakage checks before fitting."""
from pathlib import Path
from seye.core.storage import read_json, checksum
from seye.core.datasets import validate_splits
from seye.image.ingestion import load_image
from seye.recognition.features import extract
from seye.learning.prototypes import fit, evaluate


def load_samples(manifest):
    manifest = Path(manifest).resolve()
    data = read_json(manifest)
    if data.get('schema_version') != 1 or not isinstance(data.get('images'), list) or not data['images']:
        raise ValueError('Classification dataset schema required')
    if len(data['images']) > 2000:
        raise ValueError('At most 2000 classification samples')
    for row in data['images']:
        if not isinstance(row.get('label'), str) or not row['label']:
            raise ValueError('Label required')
        if row.get('annotation_status') not in ('generator', 'draft', 'human_reviewed'):
            raise ValueError('Annotation provenance required')
        if row.get('source_kind') not in ('synthetic', 'photograph', 'screenshot'):
            raise ValueError('Source kind required')
    validate_splits(data['images'], manifest.parent)
    if {r.get('split') for r in data['images']} != {'train', 'validation', 'test'}:
        raise ValueError('All three assigned splits required')
    samples = []
    for row in data['images']:
        image, _ = load_image(manifest.parent / row['path'], allowed_root=manifest.parent)
        samples.append(dict(row, features=extract(image)))
    return data, samples


def train(manifest):
    data, samples = load_samples(manifest)
    training = [r for r in samples if r['split'] == 'train']
    validation = [r for r in samples if r['split'] == 'validation']
    testing = [r for r in samples if r['split'] == 'test']
    model = fit(training, validation)
    model['dataset_sha256'] = checksum(data)
    curves = []
    for count in sorted({1, 2, max(model['training_counts'].values())}):
        subset = [r for label in model['classes'] for r in [s for s in training if s['label'] == label][:count]]
        partial = fit(subset, validation)
        curves.append({'maximum_samples_per_class': count, 'training': evaluate(partial, subset),
                       'validation': evaluate(partial, validation)})
    return model, {'schema_version': 1, 'dataset_sha256': checksum(data),
                   'training': evaluate(model, training), 'validation': evaluate(model, validation),
                   'test': evaluate(model, testing), 'learning_curves': curves,
                   'validation_used_for_rejection_thresholds': True,
                   'neural_network_training': False, 'representative_validation': False,
                   'limitations': ['Feature-based prototype learning; no pretrained or teacher weights.',
                                   'Validation scores helped choose radii and are not final held-out evidence.',
                                   'Dataset source/review provenance must be audited separately.']}


def grouped_classification_split(data, directory, seed=85):
    """Stratify indivisible content/capture components, including unknown-only evaluation."""
    import hashlib
    import json
    from seye.core.datasets import audit
    from seye.learning.prototypes import UNKNOWN
    if any('split' in row for row in data['images']):
        raise ValueError('Existing splits cannot be reassigned')
    report = audit(data['images'], directory)
    by_id = {row['id']: row for row in data['images']}
    strata = {}
    for component in report['components']:
        labels = tuple(sorted({by_id[identifier]['label'] for identifier in component}))
        if UNKNOWN in labels and labels != (UNKNOWN,):
            raise ValueError('Unknown and known content share a component; review dataset')
        strata.setdefault(labels, []).append(component)
    assigned = {}
    for labels, groups in sorted(strata.items()):
        groups.sort(key=lambda group: hashlib.sha256(json.dumps([seed, group]).encode()).hexdigest())
        if labels == (UNKNOWN,):
            if len(groups) < 2:
                raise ValueError('Unknown evaluation requires at least two components')
            splits = ['validation' if i % 2 == 0 else 'test' for i in range(len(groups))]
        else:
            if len(groups) < 3:
                raise ValueError('Every label stratum requires at least three independent components')
            splits = ['validation', 'test'] + ['train'] * (len(groups) - 2)
        for group, split in zip(groups, splits):
            assigned.update({identifier: split for identifier in group})
    output = json.loads(json.dumps(data))
    for row in output['images']:
        row['split'] = assigned[row['id']]
    output['split_provenance'] = {'seed': seed, 'method': 'content/capture-component label strata',
                                  'unknown_training_examples': 0}
    validate_splits(output['images'], directory)
    return output
