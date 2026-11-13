import importlib.util
import io
from pathlib import Path
import tarfile
import unittest
from PIL import Image

spec = importlib.util.spec_from_file_location('aloi', Path(__file__).parents[1] / 'scripts/stage88_aloi.py')
aloi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aloi)


class ALOIImportTests(unittest.TestCase):
    def archive(self, missing=False, link=False):
        output = io.BytesIO()
        png = io.BytesIO()
        Image.new('RGB', (192, 144)).save(png, format='PNG')
        payload = png.getvalue()
        with tarfile.open(fileobj=output, mode='w') as archive:
            # Traversal entries are never selected/extracted.
            extra = tarfile.TarInfo('../../outside')
            extra.size = 1
            archive.addfile(extra, io.BytesIO(b'x'))
            for c in aloi.CONDITIONS[:-1] if missing else aloi.CONDITIONS:
                member = tarfile.TarInfo(f'png4/16/16_{c}.png')
                member.size = len(payload)
                if link:
                    member.type = tarfile.SYMTYPE
                    member.linkname = '/etc/passwd'
                archive.addfile(member, io.BytesIO(payload))
        return output.getvalue()

    def test_selected_images_only(self):
        self.assertEqual(set(aloi.selected_images(self.archive(), 16)), set(aloi.CONDITIONS))

    def test_incomplete_and_links_rejected(self):
        for kwargs in ({'missing': True}, {'link': True}):
            with self.assertRaises(ValueError):
                aloi.selected_images(self.archive(**kwargs), 16)

    def test_object_labels_never_become_shape_truth(self):
        rows = [aloi.capture_row(16, c, c.encode()) for c in aloi.CONDITIONS]
        for row in rows:
            self.assertNotIn('human_confirmed', row)
            self.assertNotIn('expected_classes', row)
        report = aloi.assess(rows)
        self.assertFalse(report['ready'])
        self.assertEqual(len(report['groups']), 1)
        self.assertFalse(any('lighting conditions required' in issue or 'camera angles required' in issue for issue in report['issues']))
        self.assertFalse(report['recognition_accuracy_validated'])
