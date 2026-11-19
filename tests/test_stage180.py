import unittest,tempfile,json
from pathlib import Path
from seye.core.storage import decode_json,read_json,atomic_json,checksum
from seye.detection.annotations import validate_annotations
from seye.local.workspace import ingest,open_workspace
from PIL import Image

class WorkflowInputValidationTests(unittest.TestCase):
    def test_duplicate_nonfinite_encoding_surrogate_depth_and_byte_bombs_refused(self):
        cases=[b'{"x":1,"x":2}',b'{"outer":{"x":1,"x":2}}',b'{"x":NaN}',b'{"x":1e999}',b'{"x":"\\ud800"}',json.dumps({'x':1}).encode('utf-16'),b'['*80+b'0'+b']'*80]
        for raw in cases:
            with self.assertRaises(ValueError,msg=repr(raw[:40])):decode_json(raw)
        self.assertEqual(decode_json(b'\xef\xbb\xbf{"x":1}'),{'x':1})
        with self.assertRaises(ValueError):decode_json(b'{"x":1}',max_bytes=2)
        with self.assertRaises(ValueError):decode_json(b'{}',max_bytes=True)

    def test_boolean_annotation_schema_and_manifest_traversal_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'image.png';Image.new('RGB',(40,30),'white').save(path)
            bad=root/'annotation.json';atomic_json(bad,{'schema_version':True,'coordinate_space':'exif_oriented_source','images':[]})
            with self.assertRaises(ValueError):validate_annotations(bad)
            ingest([path],root/'workspace',root)
            manifest=root/'workspace'/'manifest.json';envelope=read_json(manifest)
            envelope['payload']['items'][0]['path']='../image.png';envelope['sha256']=checksum(envelope['payload']);atomic_json(manifest,envelope,overwrite=True)
            with self.assertRaises(ValueError):open_workspace(root/'workspace',root)
            self.assertTrue(path.is_file())

    def test_dangling_output_alias_and_cyclic_input_path_do_not_publish(self):
        from seye.local.workspace import inside
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'image.png';Image.new('RGB',(40,30),'white').save(source)
            alias=root/'alias';target=root/'new-target'
            try:alias.symlink_to(target,target_is_directory=True)
            except OSError:return
            with self.assertRaises(FileExistsError):ingest([source],alias,root)
            self.assertFalse(target.exists())
            loop=root/'loop'
            try:loop.symlink_to(loop)
            except OSError:return
            with self.assertRaises(PermissionError):inside(loop,root)
