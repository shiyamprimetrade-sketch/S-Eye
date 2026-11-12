import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw, ImageOps

import analyze_image
from seye.core.storage import atomic_json, read_json, checksum
from seye.detection.annotations import validate_annotations, evaluate_annotations
from seye.learning.prototypes import fit, predict, evaluate, save_model, load_model, UNKNOWN
from seye.recognition.features import extract


class AnnotationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        rows = []
        for n in range(2):
            image = Image.new('RGB', (300, 300), 'white')
            if n == 0:
                ImageDraw.Draw(image).ellipse((50, 50, 140, 140), outline='black', width=5)
            path = self.root / f'{n}.png'; image.save(path)
            mask = self.root / f'{n}-mask.png'; ImageOps.invert(image.convert('L')).save(mask)
            rows.append({'id': str(n), 'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'source_kind': 'synthetic', 'annotation_status': 'generator', 'annotator': 'test generator',
                         'capture_group': str(n), 'instances': [{'id': 'a', 'class': 'circle', 'box': [50, 50, 141, 141]}] if n == 0 else [],
                         'mask': mask.name, 'mask_sha256': hashlib.sha256(mask.read_bytes()).hexdigest(), 'mask_scope': 'dark_strokes'})
        self.data = {'schema_version': 1, 'coordinate_space': 'exif_oriented_source', 'images': rows}
        self.manifest = self.root / 'annotations.json'; self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.data))

    def test_scored_positive_and_negative_without_fabricated_validation(self):
        report = evaluate_annotations(self.manifest)
        self.assertEqual(report['summaries'][0]['tp'], 1)
        self.assertEqual(report['summaries'][0]['fp'], 0)
        self.assertEqual(report['summaries'][0]['fn'], 0)
        self.assertEqual(report['results'][0]['stroke_mask_iou'], 1)
        self.assertIsNone(report['results'][1]['stroke_mask_iou'])
        self.assertFalse(report['representative_validation'])

    def test_bad_box_mask_identity_and_annotation_provenance(self):
        self.data['images'][0]['instances'][0]['box'] = [0, 0, 301, 300]; self.save()
        with self.assertRaisesRegex(ValueError, 'outside'):
            validate_annotations(self.manifest)
        self.data['images'][0]['instances'][0]['box'] = [50, 50, 141, 141]
        self.data['images'][0]['mask_sha256'] = 'bad'; self.save()
        with self.assertRaisesRegex(ValueError, 'Mask identity'):
            validate_annotations(self.manifest)
        self.data['images'][0]['annotation_status'] = 'human_reviewed'; self.save()
        with self.assertRaisesRegex(ValueError, 'Generator annotations'):
            validate_annotations(self.manifest)

    def test_invalid_entire_dataset_prevents_any_inference(self):
        self.data['images'][1]['sha256'] = 'bad'; self.save()
        with patch('seye.detection.annotations.analyze') as inference:
            with self.assertRaises(ValueError):
                evaluate_annotations(self.manifest)
            inference.assert_not_called()

    def test_unsupported_semantic_class_is_scored_as_missing(self):
        self.data['images'][0]['instances'][0]['class'] = 'hand'; self.save()
        report = evaluate_annotations(self.manifest)
        self.assertEqual(report['summaries'][0]['tp'], 0)
        self.assertEqual(report['summaries'][0]['fn'], 1)
        self.assertEqual(report['summaries'][0]['fp'], 1)

    def test_pipeline_errors_remain_counted(self):
        with patch('seye.detection.annotations.analyze', side_effect=ValueError('controlled failure')):
            report = evaluate_annotations(self.manifest)
        self.assertEqual(report['summaries'][0]['pipeline_failures'], 2)
        self.assertEqual(report['summaries'][0]['attempted_images'], 2)
        self.assertIsNone(report['summaries'][0]['recall'])


class LearningTests(unittest.TestCase):
    def samples(self):
        training = [{'id': 'a', 'label': 'a', 'capture_group': 'train-a', 'features': [0., 0.]},
                    {'id': 'b', 'label': 'b', 'capture_group': 'train-b', 'features': [1., 1.]}]
        validation = [{'id': 'av', 'label': 'a', 'capture_group': 'val-a', 'features': [.02, .02]},
                      {'id': 'bv', 'label': 'b', 'capture_group': 'val-b', 'features': [.98, .98]}]
        return training, validation

    def test_independent_fit_unknown_rejection_and_checkpoint_restore(self):
        training, validation = self.samples(); model = fit(training, validation)
        self.assertEqual(model, fit(training, validation))
        self.assertFalse(model['pretrained_weights_used'])
        self.assertEqual(predict(model, [0., 0.])['label'], 'a')
        self.assertEqual(predict(model, [.5, .5])['label'], UNKNOWN)
        self.assertIsNone(predict(model, [0., 0.])['confidence_probability'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'checkpoint.json'; save_model(path, model)
            self.assertEqual(predict(load_model(path), [.98, .98]), predict(model, [.98, .98]))
            with self.assertRaises(FileExistsError):
                save_model(path, model)
            data = read_json(path); data['model']['radii']['a'] = 100; path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'integrity'):
                load_model(path)

    def test_leakage_missing_validation_and_incompatible_preprocessing(self):
        training, validation = self.samples()
        validation[0]['capture_group'] = 'train-a'
        with self.assertRaisesRegex(ValueError, 'leakage'):
            fit(training, validation)
        training, validation = self.samples()
        with self.assertRaisesRegex(ValueError, 'validation'):
            fit(training, validation[:1])
        model = fit(training, validation); model['feature_version'] = 'different'
        with self.assertRaisesRegex(ValueError, 'Incompatible'):
            predict(model, [0., 0.])

    def test_unknown_evaluation_separates_known_accuracy(self):
        training, validation = self.samples(); model = fit(training, validation)
        report = evaluate(model, [training[0], {'id': 'unknown', 'label': UNKNOWN, 'features': [.5, .5]}])
        self.assertEqual(report['known_samples'], 1)
        self.assertEqual(report['unknown_rejected'], 1)
        self.assertEqual(report['correct'], 2)

    def test_features_are_deterministic_finite_and_translation_tolerant(self):
        a, b = Image.new('RGB', (100, 100), 'white'), Image.new('RGB', (160, 130), 'white')
        ImageDraw.Draw(a).rectangle((20, 20, 60, 60), fill='black')
        ImageDraw.Draw(b).rectangle((70, 50, 110, 90), fill='black')
        self.assertEqual(extract(a), extract(b))
        self.assertEqual(extract(a), extract(a))
        self.assertGreater(len(extract(a)), 80)

    def test_atomic_json_preserves_existing_and_rejects_nonfinite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'evidence.json'; atomic_json(path, {'a': 1})
            with self.assertRaises(FileExistsError):
                atomic_json(path, {'a': 2})
            self.assertEqual(read_json(path), {'a': 1})
            with self.assertRaises(ValueError):
                checksum({'nan': float('nan')})
