import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageEnhance, PngImagePlugin

from dataset_tools import assign_splits, audit, diagnostics, validate_splits
from generalization import ROOT, digest, evaluate, load_manifest
from stage85_fixture import generate


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.manifest = generate(Path(self.temp.name) / 'photos')
        self.data = json.loads(self.manifest.read_text())

    def append_variant(self, name, transform=None, source='circle'):
        with Image.open(self.manifest.parent / f'{source}.png') as image:
            image = transform(image) if transform else image.copy()
            info = PngImagePlugin.PngInfo()
            info.add_text('variant', name)
            path = self.manifest.parent / f'{name}.png'
            image.save(path, pnginfo=info)
        row = dict(next(r for r in self.data['images'] if r['id'] == source))
        row.update(id=name, path=path.name, sha256=digest(path), capture_group=name)
        self.data['images'].append(row)
        return row

    def test_pixel_duplicate_with_different_encoded_bytes(self):
        row = self.append_variant('edited-metadata')
        self.assertNotEqual(row['sha256'], self.data['images'][0]['sha256'])
        report = audit(self.data['images'], self.manifest.parent)
        self.assertIn('decoded_duplicate', [r['reason'] for r in report['links']])

    def test_brightness_near_duplicate_and_group_assignment(self):
        self.append_variant('dim', lambda im: ImageEnhance.Brightness(im).enhance(.6))
        report = audit(self.data['images'], self.manifest.parent)
        self.assertIn('near_duplicate', [r['reason'] for r in report['links']])
        split = assign_splits(self.data, self.manifest.parent)
        by_id = {r['id']: r for r in split['images']}
        self.assertEqual(by_id['dim']['split'], by_id['circle']['split'])
        self.assertFalse(validate_splits(split['images'], self.manifest.parent)['leakage_detected'])

    def test_exact_duplicate_cross_split_rejected(self):
        duplicate = dict(self.data['images'][0], id='duplicate', capture_group='other')
        self.data['images'].append(duplicate)
        for row in self.data['images']:
            row['split'] = 'train'
        duplicate['split'] = 'test'
        report = audit(self.data['images'], self.manifest.parent)
        self.assertTrue(report['leakage_detected'])
        self.assertIn('byte_duplicate', [r['reason'] for r in report['links']])
        with self.assertRaisesRegex(ValueError, 'leakage'):
            validate_splits(self.data['images'], self.manifest.parent)

    def test_capture_group_and_transitive_connections(self):
        self.append_variant('copy')
        rows = self.data['images']
        rows[-1]['capture_group'] = rows[1]['capture_group']
        for row in rows:
            row['split'] = 'train'
        rows[1]['split'] = 'validation'
        report = audit(rows, self.manifest.parent)
        connected = next(c for c in report['components'] if 'copy' in c)
        self.assertEqual(set(connected), {'circle', 'copy', 'quadrilateral'})
        self.assertTrue(report['leakage_detected'])

    def test_splits_deterministic_under_manifest_reorder(self):
        first = assign_splits(self.data, self.manifest.parent, seed=18)
        self.data['images'].reverse()
        second = assign_splits(self.data, self.manifest.parent, seed=18)
        self.assertEqual({r['id']: r['split'] for r in first['images']},
                         {r['id']: r['split'] for r in second['images']})
        self.assertEqual(set(r['split'] for r in first['images']), {'train', 'validation', 'test'})
        self.assertNotIn('split', self.data['images'][0])

    def test_cannot_overwrite_splits(self):
        split = assign_splits(self.data, self.manifest.parent)
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            assign_splits(split, self.manifest.parent)

    def test_insufficient_components_and_bad_ratios(self):
        for row in self.data['images']:
            row['capture_group'] = 'one-session'
        with self.assertRaisesRegex(ValueError, 'at least three'):
            assign_splits(self.data, self.manifest.parent)
        for ratios in ((1, 0, 0), (.7, .2, .2), (float('nan'), .5, .5)):
            with self.assertRaisesRegex(ValueError, 'ratios'):
                assign_splits(self.data, self.manifest.parent, ratios=ratios)

    def test_partial_splits_and_hash_changes_rejected(self):
        self.data['images'][0]['split'] = 'train'
        with self.assertRaisesRegex(ValueError, 'Every image'):
            audit(self.data['images'], self.manifest.parent)
        self.data['images'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            audit(self.data['images'], self.manifest.parent)

    def test_evaluator_blocks_near_duplicate_leakage_before_inference(self):
        row = self.append_variant('dim', lambda im: ImageEnhance.Brightness(im).enhance(.6))
        for entry in self.data['images']:
            entry['split'] = 'train'
        row['split'] = 'test'
        self.manifest.write_text(json.dumps(self.data))
        with patch('generalization.run_pipeline') as inference:
            with self.assertRaisesRegex(ValueError, 'leakage'):
                evaluate(self.manifest, ('original',), split='test')
            inference.assert_not_called()

    def test_selected_split_counts_and_unestablished_validation(self):
        split = assign_splits(self.data, self.manifest.parent)
        self.manifest.write_text(json.dumps(split))
        report = evaluate(self.manifest, ('original',), split='test')
        count = sum(r['split'] == 'test' for r in split['images'])
        self.assertEqual(report['distinct_sources'], count)
        self.assertEqual(report['manifest_sources'], 4)
        self.assertEqual(report['recognition_validation_status'], 'not_established')
        self.assertEqual(report['confirmed_photographs'], 0)
        self.assertEqual(report['data_scope'], 'synthetic_only')
        self.assertTrue(all(r['split'] == 'test' for r in report['results']))
        self.assertIsNotNone(report['split_provenance'])

    def test_cli_split_and_audit_end_to_end(self):
        output = self.manifest.parent / 'split.json'
        for command, result in (('split', output), ('audit', self.manifest.parent / 'audit.json')):
            process = subprocess.run([sys.executable, str(ROOT / 'dataset_tools.py'), command,
                                      '--manifest', str(self.manifest), '--output', str(result)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
        load_manifest(output)
        process = subprocess.run([sys.executable, str(ROOT / 'dataset_tools.py'), 'split',
                                  '--manifest', str(self.manifest), '--output', str(output)], capture_output=True)
        self.assertEqual(process.returncode, 2)

    def test_confusion_matrices_and_errors_separate_pipeline_failures(self):
        rows = [dict(id='a', variant='original', source_kind='synthetic', human_confirmed=False,
                     expected_classes=['circle'], pipeline_success=True,
                     prediction={'classes': ['triangle']}, metrics={'exact_match': False}),
                dict(id='b', variant='original', source_kind='synthetic', human_confirmed=False,
                     expected_classes=['circle'], pipeline_success=False, error='controlled failure')]
        report = diagnostics(rows)
        summary = report['summaries'][0]
        self.assertEqual(summary['attempted_cases'], 2)
        self.assertEqual(summary['pipeline_failures'], 1)
        self.assertEqual(summary['binary_confusion_by_class']['circle']['fn'], 1)
        self.assertEqual(summary['binary_confusion_by_class']['triangle']['fp'], 1)
        self.assertEqual(report['error_examples'][0]['false_negative_classes'], ['circle'])
        self.assertEqual(report['error_examples'][1]['kind'], 'pipeline_error')

    def test_draft_confirmed_synthetic_and_split_results_never_mix(self):
        template = dict(id='a', variant='original', expected_classes=[], pipeline_success=True,
                        prediction={'classes': []}, metrics={'exact_match': True})
        rows = [dict(template, source_kind='synthetic', human_confirmed=False),
                dict(template, source_kind='photograph', human_confirmed=False),
                dict(template, source_kind='photograph', human_confirmed=True, split='test'),
                dict(template, source_kind='photograph', human_confirmed=True, split='train')]
        report = diagnostics(rows)
        self.assertEqual(len(report['summaries']), 4)
        self.assertTrue(all(r['attempted_cases'] == 1 for r in report['summaries']))


if __name__ == '__main__':
    unittest.main()
