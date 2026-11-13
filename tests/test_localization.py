import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

import analyze_image  # Expose src for source-checkout compatibility.
from generalization import ROOT, run_pipeline
from seye.detection.analysis import analyze
from seye.detection.metrics import box_iou, mask_iou, detection_metrics
from seye.image.ingestion import load_image
from seye.segmentation.regions import segment
from stage85_fixture import generate


def scene(path):
    image = Image.new('RGB', (300, 300), 'white')
    draw = ImageDraw.Draw(image)
    draw.ellipse((30, 40, 100, 110), outline='black', width=5)
    draw.rectangle((170, 40, 240, 110), outline='black', width=5)
    draw.polygon([(150, 180), (105, 270), (195, 270)], outline='black', width=5)
    image.save(path)
    return [{'class': 'circle', 'box': [30, 40, 101, 111]},
            {'class': 'quadrilateral', 'box': [170, 40, 241, 111]},
            {'class': 'triangle', 'box': [105, 180, 196, 271]}]


class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.photo = self.root / 'scene.png'
        self.expected = scene(self.photo)

    def test_multiple_instances_boxes_and_masks(self):
        report, images = analyze(self.photo)
        self.assertEqual(len(report['objects']), 3)
        predicted = [{'class': o['class'], 'box': o['processed_box']} for o in report['objects']]
        result = detection_metrics(self.expected, predicted, threshold=.8)
        self.assertEqual((result['tp'], result['fp'], result['fn']), (3, 0, 0))
        self.assertEqual(images['mask'].size, (300, 300))
        self.assertFalse(report['confidence_calibrated'])
        self.assertFalse(report['semantic_object_recognition'])
        self.assertTrue(all(o['uncertainty'] == 'uncalibrated_geometric_hypothesis' for o in report['objects']))

    def test_legacy_parity_including_mask_bytes(self):
        manifest = generate(self.root / 'fixtures', stress=True)
        for row in json.loads(manifest.read_text())['images']:
            path = manifest.parent / row['path']
            legacy = run_pipeline(path)
            report, images = analyze(path)
            self.assertEqual(sorted(o['label'] for o in report['objects']), sorted(legacy['labels']))
            import hashlib, io
            buffer = io.BytesIO()
            images['mask'].save(buffer, format='PNG')
            self.assertEqual(hashlib.sha256(buffer.getvalue()).hexdigest(), legacy['artifacts']['local_contrast_mask.png'])

    def test_adaptive_faint_shape_is_experimental(self):
        manifest = generate(self.root / 'fixtures', stress=True)
        path = manifest.parent / 'faint_triangle.png'
        baseline, _ = analyze(path)
        adaptive, _ = analyze(path, mode='adaptive')
        self.assertEqual(baseline['objects'], [])
        self.assertEqual([o['class'] for o in adaptive['objects']], ['triangle'])
        self.assertTrue(adaptive['experimental'])
        with self.assertRaises(ValueError):
            analyze(path, mode='unrecognized')

    def test_source_coordinates_after_resize_and_orientation(self):
        with Image.open(self.photo) as image:
            large = image.resize((600, 600))
            exif = Image.Exif()
            exif[274] = 6
            large.save(self.root / 'oriented.jpg', exif=exif)
        report, _ = analyze(self.root / 'oriented.jpg')
        self.assertEqual(report['processed_size'], [300, 300])
        self.assertEqual(report['source']['size'], [600, 600])
        self.assertEqual(len(report['objects']), 3)
        for obj in report['objects']:
            self.assertEqual(obj['source_box'], [2 * v for v in obj['processed_box']])

    def test_repeated_category_instances_are_separate(self):
        image = Image.new('RGB', (300, 300), 'white')
        draw = ImageDraw.Draw(image)
        draw.ellipse((30, 60, 100, 130), outline='black', width=5)
        draw.ellipse((170, 60, 240, 130), outline='black', width=5)
        image.save(self.photo)
        report, _ = analyze(self.photo)
        self.assertEqual([row['class'] for row in report['objects']], ['circle', 'circle'])
        self.assertNotEqual(report['objects'][0]['source_box'], report['objects'][1]['source_box'])

    def test_deterministic_region_ids(self):
        first, _ = analyze(self.photo)
        second, _ = analyze(self.photo)
        self.assertEqual(first, second)
        self.assertEqual([o['id'] for o in first['objects']], [1, 2, 3])

    def test_box_iou_and_mask_metric_conventions(self):
        self.assertEqual(box_iou([0, 0, 10, 10], [5, 0, 15, 10]), 1 / 3)
        self.assertEqual(box_iou([0, 0, 10, 10], [10, 0, 20, 10]), 0)
        empty = Image.new('L', (3, 3))
        self.assertIsNone(mask_iou(empty, empty))
        one, two = empty.copy(), empty.copy()
        one.putpixel((0, 0), 255)
        two.putpixel((0, 0), 255)
        two.putpixel((1, 0), 255)
        self.assertEqual(mask_iou(one, two), .5)
        with self.assertRaises(ValueError):
            mask_iou(empty, Image.new('L', (2, 3)))
        for box in ([0, 0, 0, 1], [0, 0, float('nan'), 1]):
            with self.assertRaises(ValueError):
                box_iou(box, [0, 0, 1, 1])

    def test_one_to_one_matching_class_errors_and_duplicate_predictions(self):
        truth = [{'class': 'circle', 'box': [0, 0, 10, 10]}]
        prediction = truth + truth + [{'class': 'triangle', 'box': [0, 0, 10, 10]}]
        result = detection_metrics(truth, prediction)
        self.assertEqual((result['tp'], result['fp'], result['fn']), (1, 2, 0))
        self.assertEqual(result['precision'], 1 / 3)
        self.assertIsNone(detection_metrics([], [])['recall'])
        for threshold in (0, True, float('nan'), 2):
            with self.assertRaises(ValueError):
                detection_metrics(truth, prediction, threshold)

    def test_matching_uses_augmenting_paths_not_greedy_counts(self):
        # First prediction can cover either truth; second only covers truth 0.
        truth = [{'class': 'circle', 'box': [0, 0, 10, 10]},
                 {'class': 'circle', 'box': [4, 0, 14, 10]}]
        prediction = [{'class': 'circle', 'box': [1, 0, 11, 10]}, truth[0]]
        self.assertEqual(detection_metrics(truth, prediction, .5)['tp'], 2)

    def test_corrupt_and_outside_root_inputs_rejected(self):
        with self.assertRaisesRegex(ValueError, 'permitted'):
            analyze(self.photo, allowed_root=self.root / 'elsewhere')
        with self.assertRaisesRegex(ValueError, 'byte limit'):
            load_image(self.photo, max_bytes=1)
        with self.assertRaisesRegex(ValueError, 'pixel limit'):
            load_image(self.photo, max_pixels=100)
        invalid = self.root / 'invalid.jpg'
        invalid.write_bytes(b'bad jpeg')
        with self.assertRaisesRegex(ValueError, 'decoding failed'):
            analyze(invalid)
        gif = self.root / 'disguised.png'
        Image.new('RGB', (3, 3)).save(gif, format='GIF')
        with self.assertRaisesRegex(ValueError, 'content must be'):
            analyze(gif)

    def test_cli_creates_private_outputs_and_preserves_existing_directory(self):
        destination = self.root / 'results'
        command = [sys.executable, str(ROOT / 'analyze_image.py'), '--image', str(self.photo),
                   '--output-dir', str(destination), '--allowed-root', str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in destination.iterdir()}, {'analysis.json', 'mask.png', 'grouped_mask.png', 'overlay.png'})
        self.assertEqual(len(json.loads((destination / 'analysis.json').read_text())['objects']), 3)
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
