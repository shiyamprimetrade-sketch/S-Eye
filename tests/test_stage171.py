import unittest,tempfile,hashlib
from pathlib import Path
from PIL import Image
from seye.local.workspace import ingest,open_workspace

class WorkspaceTests(unittest.TestCase):
    def test_import_detaches_sources_preserves_bytes_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);image=root/'input.png';Image.new('RGB',(50,40),'white').save(image);original=image.read_bytes()
            receipt=ingest([image],root/'workspace',root);_,manifest,digest=open_workspace(root/'workspace',root)
            self.assertEqual(receipt['manifest_sha256'],digest)
            self.assertEqual((root/'workspace'/manifest['items'][0]['path']).read_bytes(),original)
            with self.assertRaises(FileExistsError):ingest([image],root/'workspace',root)
            image.unlink();self.assertEqual(open_workspace(root/'workspace',root)[1]['items'][0]['source']['sha256'],hashlib.sha256(original).hexdigest())

    def test_invalid_late_source_does_not_publish_and_snapshot_corruption_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);good=root/'good.png';bad=root/'bad.png';Image.new('RGB',(40,30)).save(good);bad.write_bytes(b'broken')
            with self.assertRaises(ValueError):ingest([good,bad],root/'failed',root)
            self.assertFalse((root/'failed').exists());self.assertEqual(list(root.glob('.seye-local-*')),[])
            ingest([good],root/'workspace',root);(root/'workspace'/'images'/'0001.png').write_bytes(b'changed')
            with self.assertRaises(ValueError):open_workspace(root/'workspace',root)
