import shutil
import unittest
from seye.video.interface import generated_probe, observe_video
from seye.integration.service import execute, Permissions

class PrerecordedInterfaceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
    def test_actual_clip_encode_decode(self):
        result = generated_probe()
        self.assertEqual(result['frames'], 4)
        self.assertEqual(result['timestamps'], [0.0, .5, 1.0, 1.5])
        self.assertTrue(result['source_preserved'])
        self.assertFalse(result['automatic_action_authorized'])

    def test_limits_and_permission_precede_decode(self):
        for fps in (True, 0, 5, 100):
            with self.assertRaises(ValueError): observe_video('missing.mp4', '.', fps=fps)
        with self.assertRaises(PermissionError):
            execute({'schema_version':1,'request_id':'test','action':'interface_video','video':'missing.mp4'}, Permissions())
        with self.assertRaises(ValueError): observe_video('/missing.mp4', '/elsewhere')
