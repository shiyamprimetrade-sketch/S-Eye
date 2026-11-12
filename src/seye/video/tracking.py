"""Deterministic box tracking for prerecorded observations; bounded missed-frame retention."""
from seye.detection.metrics import detection_metrics, valid_box


class Tracker:
    def __init__(self, max_missed=2, iou_threshold=.2):
        if type(max_missed) is not int or not 0 <= max_missed <= 100:
            raise ValueError('Invalid missed-frame limit')
        detection_metrics([], [], iou_threshold)
        self.max_missed, self.threshold = max_missed, iou_threshold
        self.tracks, self.next_id, self.last_timestamp = {}, 1, None

    def update(self, detections, timestamp):
        import math
        if type(timestamp) not in (int, float) or not math.isfinite(timestamp) or timestamp < 0 or (self.last_timestamp is not None and timestamp <= self.last_timestamp):
            raise ValueError('Strictly increasing finite nonnegative timestamps required')
        for detection in detections:
            valid_box(detection['box'])
        ids = sorted(self.tracks)
        expected = []
        for identifier in ids:
            track = self.tracks[identifier]
            dt = timestamp - track['last_seen']
            shift = [track['velocity'][axis] * dt for axis in (0, 1)]
            expected.append({'class': track['class'], 'box': [track['box'][0] + shift[0], track['box'][1] + shift[1], track['box'][2] + shift[0], track['box'][3] + shift[1]]})
        matching = detection_metrics(expected, detections, self.threshold)['matches']
        matched_tracks, matched_detections = set(), set()
        visible = []
        for match in matching:
            identifier, index = ids[match['expected']], match['predicted']
            track, detection = self.tracks[identifier], detections[index]
            dt = timestamp - track['last_seen']
            velocity = [((detection['box'][axis] + detection['box'][axis + 2]) - (track['box'][axis] + track['box'][axis + 2])) / (2 * dt) for axis in (0, 1)]
            track.update(box=list(detection['box']), velocity=velocity, last_seen=timestamp, missed=0)
            visible.append({'track_id': identifier, 'class': track['class'], 'box': track['box']})
            matched_tracks.add(identifier); matched_detections.add(index)
        for identifier in ids:
            if identifier not in matched_tracks:
                self.tracks[identifier]['missed'] += 1
                if self.tracks[identifier]['missed'] > self.max_missed:
                    del self.tracks[identifier]
        for index, detection in enumerate(detections):
            if index not in matched_detections:
                if len(self.tracks) >= 256:
                    raise ValueError('Tracking capacity exceeded')
                identifier = self.next_id; self.next_id += 1
                self.tracks[identifier] = {'class': detection['class'], 'box': list(detection['box']),
                                           'velocity': [0., 0.], 'last_seen': timestamp, 'missed': 0}
                visible.append({'track_id': identifier, 'class': detection['class'], 'box': list(detection['box'])})
        self.last_timestamp = timestamp
        return {'timestamp': timestamp, 'visible': sorted(visible, key=lambda row: row['track_id']),
                'retained_occluded_ids': sorted(set(self.tracks) - {r['track_id'] for r in visible})}
