"""Evidence-grounded spatial inventories and one-to-one geometric scene changes."""
from seye.detection.metrics import valid_box, detection_metrics


def inventory(objects):
    if len(objects) > 256:
        raise ValueError('Scene object limit exceeded')
    rows = []
    for index, obj in enumerate(objects):
        box = obj.get('box', obj.get('source_box'))
        valid_box(box)
        label = obj.get('class', 'unknown')
        if not isinstance(label, str) or not label:
            raise ValueError('Object evidence label required')
        rows.append({'id': index, 'class': label, 'box': list(box)})
    relations = []
    for first in rows:
        for second in rows[first['id'] + 1:]:
            a, b = first['box'], second['box']
            horizontal = 'left_of' if (a[0] + a[2]) < (b[0] + b[2]) else ('right_of' if (a[0] + a[2]) > (b[0] + b[2]) else 'horizontally_aligned')
            vertical = 'above' if (a[1] + a[3]) < (b[1] + b[3]) else ('below' if (a[1] + a[3]) > (b[1] + b[3]) else 'vertically_aligned')
            relations.append({'first': first['id'], 'second': second['id'], 'horizontal': horizontal, 'vertical': vertical})
    return {'schema_version': 1, 'objects': rows, 'relations': relations,
            'description': f"{len(rows)} geometric hypotheses; semantic identities unverified."}


def compare(before, after, threshold=.3):
    first, second = inventory(before)['objects'], inventory(after)['objects']
    matches = detection_metrics(first, second, threshold)['matches']
    old, new = {m['expected'] for m in matches}, {m['predicted'] for m in matches}
    return {'schema_version': 1, 'matched': matches,
            'missing': [r for i, r in enumerate(first) if i not in old],
            'appeared': [r for i, r in enumerate(second) if i not in new],
            'similarity': len(matches) / max(len(first), len(second)) if first or second else 1.,
            'scope': 'class-aware box overlap; disappearance is not semantic certainty'}


def group_objects(objects, maximum_gap=20):
    """Connected proximity groups, not semantic groups or identity assertions."""
    import math
    if type(maximum_gap) not in (int, float) or not math.isfinite(maximum_gap) or maximum_gap < 0:
        raise ValueError('Finite nonnegative grouping gap required')
    rows = inventory(objects)['objects']; parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i

    for first in range(len(rows)):
        for second in range(first + 1, len(rows)):
            a, b = rows[first]['box'], rows[second]['box']
            dx, dy = max(0, a[0]-b[2], b[0]-a[2]), max(0, a[1]-b[3], b[1]-a[3])
            if math.hypot(dx, dy) <= maximum_gap:
                x, y = find(first), find(second); parent[max(x,y)] = min(x,y)
    groups = {}
    for index, row in enumerate(rows):
        groups.setdefault(find(index), []).append(row['id'])
    return {'groups': [members for _, members in sorted(groups.items())], 'maximum_gap': maximum_gap,
            'scope': 'connected box proximity; group members are not asserted to be the same object'}
