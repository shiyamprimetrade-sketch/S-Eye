import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw

import analyze_image
from seye.core.probes import probe, sha256, validate_manifest


class RealInputProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        image = Image.new('RGB', (120, 120), 'white')
        ImageDraw.Draw(image).rectangle((30, 30, 90, 90), outline='black', width=3)
        image.save(self.root / 'fixture.png')
        self.data = {'schema_version': 1, 'annotation_status': 'unlabelled', 'images': [
            {'id': 'fixture', 'path': 'fixture.png', 'sha256': sha256(self.root / 'fixture.png'), 'source_kind': 'screenshot'}]}
        self.manifest = self.root / 'manifest.json'
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.data))

    def test_actual_execution_has_no_accuracy_claim_and_is_repeatable(self):
        report = probe(self.manifest, variants=('original',), repeats=2)
        self.assertEqual(report['successful_runs'], 4)
        self.assertEqual(report['source_counts'], {'screenshot': 1})
        self.assertIsNone(report['recognition_accuracy'])
        self.assertIsNone(report['localization_accuracy'])
        self.assertFalse(report['representative_generalization_validated'])
        self.assertFalse(report['semantic_recognition_evaluated'])
        self.assertTrue(all(r['stable_predictions'] for r in report['repeatability']))
        self.assertTrue(all(r['stable_mask_pixels'] for r in report['repeatability']))

    def test_ground_truth_claims_are_rejected(self):
        for key, value in [('expected_classes', []), ('human_confirmed', True), ('ground_truth', {})]:
            self.data['images'][0][key] = value
            self.save()
            with self.assertRaisesRegex(ValueError, 'cannot assert'):
                validate_manifest(self.manifest)
            del self.data['images'][0][key]

    def test_validate_all_sources_before_inference(self):
        self.data['images'].append(dict(self.data['images'][0], id='changed', sha256='0' * 64))
        self.save()
        with patch('seye.core.probes.analyze') as inference:
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                probe(self.manifest)
            inference.assert_not_called()

    def test_failures_count_and_stability_is_not_invented(self):
        with patch('seye.core.probes.analyze', side_effect=ValueError('controlled rejection')):
            report = probe(self.manifest, variants=('original',))
        self.assertEqual(report['attempted_runs'], 4)
        self.assertEqual(report['successful_runs'], 0)
        self.assertTrue(all(not r['all_completed'] for r in report['repeatability']))
        self.assertTrue(all(r['stable_predictions'] is None for r in report['repeatability']))
        self.assertIsNone(report['recognition_accuracy'])

    def test_one_repeat_does_not_claim_stability(self):
        report = probe(self.manifest, variants=('original',), repeats=1)
        self.assertTrue(all(r['stable_predictions'] is None for r in report['repeatability']))

    def test_source_kind_and_root_escape_rejected(self):
        self.data['images'][0]['source_kind'] = 'synthetic'
        self.save()
        with self.assertRaisesRegex(ValueError, 'photograph or screenshot'):
            validate_manifest(self.manifest)
        self.data['images'][0].update(source_kind='photograph', path='../outside.png')
        self.save()
        with self.assertRaisesRegex(ValueError, 'permitted source root'):
            validate_manifest(self.manifest)

    def test_overlay_filenames_do_not_use_untrusted_ids(self):
        self.data['images'][0]['id'] = '../../escape'
        self.save()
        directory = self.root / 'overlays'
        probe(self.manifest, variants=('original',), repeats=1, overlay_directory=directory)
        self.assertEqual({p.name for p in directory.iterdir()}, {'000_baseline.jpg', '000_adaptive.jpg'})
        with self.assertRaises(FileExistsError):
            probe(self.manifest, variants=('original',), overlay_directory=directory)

    def test_invalid_probe_configuration(self):
        for repeats in (0, True, 6):
            with self.assertRaises(ValueError):
                probe(self.manifest, repeats=repeats)
        for variants in (('original', 'original'), ('dim',)):
            with self.assertRaises(ValueError):
                probe(self.manifest, variants=variants)


if __name__ == '__main__':
    unittest.main()
