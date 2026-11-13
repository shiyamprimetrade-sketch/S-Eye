"""Half-open box IoU, binary-mask IoU and class-aware one-to-one matching."""
import math


def valid_box(box):
    if not isinstance(box, (list, tuple)) or len(box) != 4 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in box):
        raise ValueError('Box requires four finite coordinates')
    if box[2] <= box[0] or box[3] <= box[1]:
        raise ValueError('Box area must be positive')


def box_iou(first, second):
    valid_box(first)
    valid_box(second)
    intersection = max(0, min(first[2], second[2]) - max(first[0], second[0])) * max(0, min(first[3], second[3]) - max(first[1], second[1]))
    area_a = (first[2] - first[0]) * (first[3] - first[1])
    area_b = (second[2] - second[0]) * (second[3] - second[1])
    return intersection / (area_a + area_b - intersection)


def mask_iou(first, second):
    if first.size != second.size:
        raise ValueError('Masks must use the same pixel grid')
    pixels = zip(first.convert('L').get_flattened_data(), second.convert('L').get_flattened_data())
    intersection = union = 0
    for a, b in pixels:
        intersection += bool(a) and bool(b)
        union += bool(a) or bool(b)
    return intersection / union if union else None


def detection_metrics(expected, predicted, threshold=.5):
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or not 0 < threshold <= 1:
        raise ValueError('IoU threshold must be finite and in (0,1]')
    if len(expected) > 256 or len(predicted) > 256:
        raise ValueError('At most 256 detections per side are supported by this matcher')
    for row in expected + predicted:
        valid_box(row['box'])
        if not isinstance(row['class'], str) or not row['class']:
            raise ValueError('Each detection requires a class')
    adjacency = {}
    for p, prediction in enumerate(predicted):
        possible = [(box_iou(prediction['box'], truth['box']), t) for t, truth in enumerate(expected)
                    if prediction['class'] == truth['class']]
        adjacency[p] = [t for value, t in sorted(possible, reverse=True) if value >= threshold]
    # Maximum-cardinality bipartite match; duplicate predictions cannot inflate TP.
    owners = {}

    def augment(prediction, visited):
        for truth in adjacency[prediction]:
            if truth in visited:
                continue
            visited.add(truth)
            if truth not in owners or augment(owners[truth], visited):
                owners[truth] = prediction
                return True
        return False

    for prediction in range(len(predicted)):
        augment(prediction, set())
    matches = [{'expected': t, 'predicted': p, 'iou': box_iou(expected[t]['box'], predicted[p]['box'])}
               for t, p in sorted(owners.items())]
    tp, fp, fn = len(matches), len(predicted) - len(matches), len(expected) - len(matches)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'iou_threshold': threshold, 'matches': matches,
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None}
