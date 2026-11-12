import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from PIL import Image

from generalization import (ROOT, VARIANTS, class_metrics, digest, evaluate,
                            load_manifest, normalize, run_pipeline, transform)
from stage85_fixture import generate


class GeneralizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = generate(self.root / 'dataset')

    def mutate(self, change):
        data = json.loads(self.manifest.read_text())
        change(data['images'])
        self.manifest.write_text(json.dumps(data))

    def test_legacy_quadrilateral_taxonomy(self):
        for name in ('Square-like', 'Rectangle-like', 'Ambiguous quadrilateral'):
            self.assertEqual(normalize(name), 'quadrilateral')
        self.assertEqual(normalize('unrecognized'), 'unknown')

    def test_presence_metrics_duplicates_unknown_and_empty(self):
        self.assertEqual(class_metrics(['circle'], ['circle', 'circle'])['precision'], 1)
        self.assertEqual(class_metrics(['circle'], ['circle', 'unknown'])['precision'], .5)
        self.assertEqual(class_metrics(['circle'], [])['recall'], 0)
        self.assertIsNone(class_metrics([], [])['precision'])
        self.assertTrue(class_metrics([], [])['exact_match'])
        self.assertFalse(class_metrics([], ['unknown'])['exact_match'])

    def test_hash_mismatch_rejected_before_analysis(self):
        (self.manifest.parent / 'circle.png').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            evaluate(self.manifest)

    def test_duplicate_photographs_rejected(self):
        self.mutate(lambda rows: rows.append(dict(rows[0], id='duplicate')))
        with self.assertRaisesRegex(ValueError, 'Duplicate source'):
            load_manifest(self.manifest)

    def test_invalid_taxonomy_rejected(self):
        self.mutate(lambda rows: rows[0].update(expected_classes=['wardrobe']))
        with self.assertRaisesRegex(ValueError, 'unique labels'):
            load_manifest(self.manifest)

    def test_non_boolean_confirmation_rejected(self):
        self.mutate(lambda rows: rows[0].update(human_confirmed='false'))
        with self.assertRaisesRegex(ValueError, 'boolean'):
            load_manifest(self.manifest)

    def test_synthetic_confirmation_rejected(self):
        self.mutate(lambda rows: rows[0].update(human_confirmed=True))
        with self.assertRaisesRegex(ValueError, 'Synthetic labels'):
            load_manifest(self.manifest)

    def test_path_escape_rejected(self):
        self.mutate(lambda rows: rows[0].update(path='../outside.png'))
        with self.assertRaisesRegex(ValueError, 'inside'):
            load_manifest(self.manifest)

    def test_transform_determinism_and_no_input_mutation(self):
        with Image.open(self.manifest.parent / 'triangle.png') as source:
            before = source.tobytes()
            for variant in VARIANTS:
                self.assertEqual(transform(source, variant).tobytes(), transform(source, variant).tobytes())
            self.assertEqual(source.tobytes(), before)
            with self.assertRaises(ValueError):
                transform(source, 'invalid')

    def test_original_uses_actual_source_bytes(self):
        # A JPEG with EXIF orientation exercises original-byte and orientation provenance.
        source = self.manifest.parent / 'circle.png'
        with Image.open(source) as image:
            exif = Image.Exif()
            exif[274] = 6
            image.save(self.manifest.parent / 'oriented.jpg', exif=exif)
        self.mutate(lambda rows: rows[0].update(path='oriented.jpg', sha256=digest(self.manifest.parent / 'oriented.jpg')))
        report = evaluate(self.manifest, ('original',))
        self.assertEqual(report['results'][0]['input_sha256'], digest(self.manifest.parent / 'oriented.jpg'))

    def test_camera_pipeline_reproducible_and_isolated(self):
        source = self.manifest.parent / 'triangle.png'
        original_hash = digest(source)
        repo_before = {p.name: digest(p) for p in ROOT.iterdir() if p.is_file()}
        first, second = run_pipeline(source), run_pipeline(source)
        self.assertEqual(first['classes'], ['triangle'])
        self.assertEqual(first, second)
        self.assertEqual(digest(source), original_hash)
        self.assertEqual(repo_before, {p.name: digest(p) for p in ROOT.iterdir() if p.is_file()})

    def test_corrupt_input_and_blank_negative_control(self):
        broken = self.root / 'broken.jpg'
        broken.write_bytes(b'not an image')
        with self.assertRaises(RuntimeError):
            run_pipeline(broken)
        self.assertEqual(run_pipeline(self.manifest.parent / 'blank.png')['labels'], [])

    def test_report_counts_sources_and_separates_evidence(self):
        report = evaluate(self.manifest, ('original', 'dim'))
        self.assertEqual(report['distinct_sources'], 4)
        self.assertEqual(report['confirmed_photographs'], 0)
        self.assertEqual(len(report['results']), 8)
        self.assertEqual(len(report['summary']), 2)
        self.assertTrue(all(r['pipeline_success'] for r in report['results']))
        self.assertTrue(all(r['metrics']['exact_match'] for r in report['results']))
        self.assertFalse(report['localization_evaluated'])
        self.assertEqual(set(report['pipeline_sha256']), {'local_contrast.py', 'group_shapes.py', 'filter_regions.py', 'classify_camera_v2.py'})

    def test_cli_preserves_existing_report(self):
        output = self.root / 'report.json'
        output.write_text('existing evidence')
        result = subprocess.run([sys.executable, str(ROOT / 'generalization.py'),
                                 '--manifest', str(self.manifest), '--output', str(output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(output.read_text(), 'existing evidence')

    def test_pipeline_failures_remain_in_denominator(self):
        with patch('generalization.run_pipeline', side_effect=RuntimeError('controlled failure')):
            report = evaluate(self.manifest, ('original',))
        self.assertEqual(report['summary'][0]['cases'], 4)
        self.assertEqual(report['summary'][0]['pipeline_failures'], 4)
        self.assertEqual(report['summary'][0]['exact_matches'], 0)

    def test_invalid_row_and_nested_class_rejected(self):
        self.mutate(lambda rows: rows[0].update(expected_classes=[[]]))
        with self.assertRaises(ValueError):
            load_manifest(self.manifest)
        self.mutate(lambda rows: rows.append(None))
        with self.assertRaises(ValueError):
            load_manifest(self.manifest)

    def test_duplicate_variants_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unique supported'):
            evaluate(self.manifest, ('original', 'original'))


if __name__ == '__main__':
    unittest.main()
