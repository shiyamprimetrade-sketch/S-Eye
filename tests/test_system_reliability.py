import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from PIL import Image, ImageDraw
import analyze_image
from seye.core.storage import atomic_json, read_json
from seye.learning.dataset import grouped_classification_split
from seye.memory.store import Memory
from seye.recognition.features import FEATURE_VERSION
from seye.segmentation.experimental import edges, denoise, reconstruct, convex_boundary, projection_split
from seye.integration.service import Permissions, handle, bounded_handle
from seye.video.ingestion import analyze_video


class ReliabilityTests(unittest.TestCase):
    def test_denoise_boundary_reconstruction_and_conservative_split(self):
        image = Image.new('L', (100, 60)); draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 35, 45), fill=255); draw.rectangle((65, 10, 90, 45), fill=255)
        draw.line((35, 27, 65, 27), fill=255)
        self.assertEqual(len(projection_split(image)), 2)
        self.assertGreaterEqual(len(convex_boundary(image)), 4)
        dot = Image.new('L', (30, 30)); dot.putpixel((15, 15), 255)
        self.assertIsNone(denoise(dot).getbbox())
        self.assertIsNotNone(edges(image).getbbox())
        self.assertEqual(reconstruct(image).size, image.size)
        self.assertEqual(len(projection_split(Image.new('L', (10, 10)))), 1)

    def test_read_only_memory_and_permissioned_retrieval_do_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / 'memory.sqlite3'
            memory = Memory(path)
            record = {'schema_version': 1, 'features': [0.], 'feature_version': FEATURE_VERSION, 'provenance': {}}
            memory.put(record); memory.close(); before = path.read_bytes()
            readonly = Memory(path, read_only=True)
            self.assertEqual(len(readonly.search([0.])), 1)
            with self.assertRaises(PermissionError):
                readonly.put(record)
            readonly.close(); self.assertEqual(path.read_bytes(), before)

    def test_workflow_cli_has_explicit_roots_and_atomic_response(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); image = root / 'image.png'; Image.new('RGB', (30, 30), 'white').save(image)
            request = root / 'request.json'; atomic_json(request, {'schema_version': 1, 'request_id': 'cli', 'action': 'analyze', 'image': str(image)})
            output = root / 'response.json'
            command = [sys.executable, '-m', 'seye.api.workflow', '--request', str(request), '--output', str(output),
                       '--read-root', str(root), '--write-root', str(root)]
            # Explicit source path for the checkout smoke; installed counterpart is exercised in CI.
            env = dict(__import__('os').environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / 'src'))
            result = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(read_json(output)['success'])
            self.assertEqual(subprocess.run(command, capture_output=True, env=env).returncode, 2)

    def test_bounded_worker_deadline_and_unsupported_action(self):
        response = bounded_handle({'schema_version': 1, 'request_id': 'deadline', 'action': 'analyze', 'image': 'absent.png'},
                                  Permissions(), timeout=.000001)
        self.assertFalse(response['success'])
        self.assertEqual(response['error']['type'], 'Timeout')
        response = bounded_handle({'schema_version': 1, 'request_id': 'unsupported', 'action': 'network'}, Permissions(), timeout=5)
        self.assertFalse(response['success'])
        self.assertEqual(response['error']['type'], 'ValueError')
        with self.assertRaises(ValueError):
            bounded_handle({}, Permissions(), timeout=0)

    def test_annotation_templates_cannot_be_scored_as_negative_truth(self):
        from seye.detection.annotations import validate_annotations
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); Image.new('RGB', (20, 20), 'white').save(root / 'source.png')
            script = Path(__file__).resolve().parents[1] / 'scripts/create_annotations.py'
            result = subprocess.run([sys.executable, str(script), '--directory', str(root), '--output', str(root / 'annotations.json'),
                                     '--source-kind', 'photograph', '--annotator', 'test template'], capture_output=True)
            self.assertEqual(result.returncode, 0)
            with self.assertRaisesRegex(ValueError, 'reviewed'):
                validate_annotations(root / 'annotations.json')

    def test_permission_boundary_blocks_symlink_escapes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); allowed = root / 'allowed'; allowed.mkdir()
            outside = root / 'outside.png'; Image.new('RGB', (10, 10)).save(outside)
            (allowed / 'escape.png').symlink_to(outside)
            result = handle({'schema_version': 1, 'request_id': 'x', 'action': 'analyze', 'image': str(allowed / 'escape.png')},
                            Permissions((str(allowed),), ()))
            self.assertFalse(result['success'])
            self.assertEqual(result['error']['type'], 'PermissionError')

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'Optional ffmpeg tools unavailable')
    def test_prerecorded_mp4_ingestion_and_controlled_tracking(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for n in range(3):
                image = Image.new('RGB', (160, 120), 'white')
                ImageDraw.Draw(image).ellipse((30+n*3, 30, 80+n*3, 80), outline='black', width=5)
                image.save(root / f'{n:02d}.png')
            path = root / 'video.mp4'
            encoded = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-framerate', '2', '-i', str(root / '%02d.png'),
                                      '-c:v', 'mpeg4', str(path)], capture_output=True, timeout=20)
            self.assertEqual(encoded.returncode, 0)
            report = analyze_video(path, root, fps=2, max_seconds=2)
            self.assertEqual(report['processed_frames'], 3)
            ids = [frame['visible'][0]['track_id'] for frame in report['frames']]
            self.assertEqual(len(set(ids)), 1)
            self.assertGreater(report['observed_frames_per_second'], 0)
            with self.assertRaises(ValueError):
                analyze_video(path, root / 'not-permitted')

class ReleaseGateTests(unittest.TestCase):
    def test_all_stages_are_tracked_and_unmet_v1_release_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        stages = read_json(root / 'tasks/stages_086_199.json')['stages']
        self.assertEqual([r['stage'] for r in stages], list(range(86, 200)))
        self.assertTrue(all(row.get('completion_scope') and row.get('evidence_paths') for row in stages if row['completion_declared']))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'release.json'
            result = subprocess.run([sys.executable, str(root / 'scripts/release_audit.py'), '--output', str(output), '--require-release'], capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(read_json(output)['release_ready'])
