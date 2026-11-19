import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from PIL import Image, ImageDraw
import analyze_image
from seye.core.storage import atomic_json, checksum, read_json
from seye.memory.store import Memory
from seye.recognition.features import FEATURE_VERSION
from seye.scenes.relations import inventory, compare
from seye.video.tracking import Tracker
from seye.integration.service import Permissions, handle


def observation(value, label):
    return {'schema_version': 1, 'features': [value, value], 'feature_version': FEATURE_VERSION,
            'provenance': {'label': label, 'source_sha256': str(value)}}


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.memory = Memory(self.root / 'memory.sqlite3'); self.addCleanup(self.memory.close)

    def test_content_identity_retrieval_and_verified_export_restore(self):
        first = self.memory.put(observation(0, 'a'))
        self.assertEqual(first, self.memory.put(observation(0, 'a')))
        self.memory.put(observation(1, 'b'))
        self.assertEqual(self.memory.search([.05, .05])[0]['id'], first)
        self.assertEqual(self.memory.verify()['verified_observations'], 2)
        self.memory.export(self.root / 'export.json')
        other = Memory(self.root / 'restored.sqlite3'); self.addCleanup(other.close)
        self.assertEqual(other.import_file(self.root / 'export.json')['verified_observations'], 2)
        self.assertEqual(other.get(first), self.memory.get(first))

    def test_import_failure_rolls_back_and_corruption_is_detected(self):
        self.memory.put(observation(0, 'original'))
        payload = {'schema_version': 1, 'observations': [observation(1, 'new'), {'schema_version': 1, 'features': [0], 'provenance': {}}]}
        atomic_json(self.root / 'bad.json', {'payload': payload, 'sha256': checksum(payload)})
        with self.assertRaises(ValueError):
            self.memory.import_file(self.root / 'bad.json')
        self.assertEqual(self.memory.verify()['verified_observations'], 1)
        self.memory.db.execute("UPDATE observations SET payload='{}'"); self.memory.db.commit()
        with self.assertRaises(ValueError):
            self.memory.verify()

    def test_legacy_import_is_lossless_and_has_no_invented_features(self):
        original = {'schema_version': 2, 'objects': [{'label': 'Circle-like'}], 'photo': 'old.jpg'}
        source = self.root / 'legacy.jsonl'; source.write_text('\n\n' + json.dumps(original) + '\n')
        before = source.read_bytes(); self.assertEqual(self.memory.import_legacy_jsonl(source), 1)
        exported = self.root / 'legacy-export.json'; self.memory.export(exported)
        record = read_json(exported)['payload']['observations'][0]
        self.assertEqual(record['legacy_payload'], original)
        self.assertEqual(record['provenance']['line'], 3)
        self.assertIsNone(record['features'])
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(self.memory.search([0, 0]), [])

    def test_explicit_retention_and_unrelated_database_protection(self):
        self.memory.put(observation(0, 'a')); newest = self.memory.put(observation(1, 'b'))
        self.assertEqual(self.memory.retain(1), 1)
        self.assertIsNotNone(self.memory.get(newest))
        path = self.root / 'unrelated.sqlite3'; db = sqlite3.connect(path)
        db.execute('CREATE TABLE unrelated (id INTEGER)'); db.commit(); db.close()
        with self.assertRaisesRegex(ValueError, 'unrelated'):
            Memory(path)


class SceneTrackingTests(unittest.TestCase):
    def test_spatial_evidence_and_missing_appeared_objects(self):
        a = {'class': 'circle', 'box': [0, 0, 10, 10]}
        b = {'class': 'triangle', 'box': [30, 30, 40, 40]}
        scene = inventory([a, b]); self.assertEqual(scene['relations'][0]['horizontal'], 'left_of')
        self.assertEqual(scene['relations'][0]['vertical'], 'above')
        change = compare([a, b], [a]); self.assertEqual(change['missing'][0]['class'], 'triangle')
        self.assertEqual(change['appeared'], [])

    def test_tracking_motion_occlusion_and_expiry(self):
        tracker = Tracker(max_missed=1)
        a = lambda x: {'class': 'circle', 'box': [x, 0, x + 20, 20]}
        first = tracker.update([a(0)], 0)['visible'][0]['track_id']
        self.assertEqual(tracker.update([a(5)], 1)['visible'][0]['track_id'], first)
        self.assertEqual(tracker.update([], 2)['retained_occluded_ids'], [first])
        self.assertEqual(tracker.update([a(15)], 3)['visible'][0]['track_id'], first)
        tracker.update([], 4); tracker.update([], 5)
        self.assertNotEqual(tracker.update([a(30)], 6)['visible'][0]['track_id'], first)
        with self.assertRaises(ValueError):
            tracker.update([], 6)

    def test_repeated_category_track_ids_are_unique(self):
        tracker = Tracker()
        rows = [{'class': 'circle', 'box': [0, 0, 20, 20]}, {'class': 'circle', 'box': [80, 0, 100, 20]}]
        first = tracker.update(rows, 0)
        second = tracker.update(list(reversed(rows)), 1)
        self.assertEqual({r['track_id'] for r in first['visible']}, {r['track_id'] for r in second['visible']})
        self.assertEqual(len(second['visible']), 2)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        image = Image.new('RGB', (200, 200), 'white')
        ImageDraw.Draw(image).ellipse((50, 50, 150, 150), outline='black', width=5)
        self.image = self.root / 'circle.png'; image.save(self.image)
        self.grants = Permissions((str(self.root),), (str(self.root),), memory=True)

    def request(self, action, **extra):
        return {'schema_version': 1, 'request_id': 'test', 'action': action, 'image': str(self.image), **extra}

    def test_analysis_memory_round_trip_and_grounded_question(self):
        response = handle(self.request('analyze'), self.grants)
        self.assertTrue(response['success'])
        memory = str(self.root / 'observations.sqlite3')
        saved = handle(self.request('remember', memory=memory), self.grants)
        self.assertTrue(saved['success'])
        retrieved = handle(self.request('retrieve', memory=memory), self.grants)
        self.assertEqual(retrieved['result']['matches'][0]['id'], saved['result']['observation_id'])
        self.assertEqual(handle(self.request('visual_question', question='count_geometric_regions'), self.grants)['result']['answer'], 1)
        self.assertIsNone(handle(self.request('visual_question', question='Whose hand is this?'), self.grants)['result']['answer'])

    def test_permissions_deny_ungranted_paths_and_capabilities(self):
        self.assertFalse(handle(self.request('analyze'), Permissions())['success'])
        self.assertFalse(handle(self.request('remember', memory=str(self.root / 'memory.sqlite3')),
                                Permissions((str(self.root),), (str(self.root),)))['success'])
        self.assertFalse(handle({'schema_version': 1, 'request_id': 'x', 'action': 'camera'}, self.grants)['success'])
        self.assertFalse(handle(self.request('video', video='/tmp/movie.mp4'), self.grants)['success'])
