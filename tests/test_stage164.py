import unittest,tempfile,os
from pathlib import Path
from seye.api import Permissions
from seye.integration.boundaries import plan_reads

class BoundaryTests(unittest.TestCase):
    def test_false_string_capabilities_empty_roots_and_special_files_refused(self):
        for value in ('false',1,None):
            with self.assertRaises(ValueError):Permissions(memory=value)
        with self.assertRaises(ValueError):Permissions(read_roots=('',))
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);permissions=Permissions((root,))
            with self.assertRaises(PermissionError):permissions.require(root)
            if hasattr(os,'mkfifo'):
                fifo=root/'pipe';os.mkfifo(fifo)
                with self.assertRaises(PermissionError):permissions.require(fifo)

    def test_traversal_symlink_escape_and_changed_source_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'allowed';root.mkdir();outside=Path(directory)/'outside';outside.write_text('outside')
            path=root/'input.png';path.write_text('first');permissions=Permissions((root,))
            with self.assertRaises(PermissionError):permissions.require(root/'..'/'outside')
            try:(root/'link').symlink_to(outside)
            except OSError:pass
            else:
                with self.assertRaises(PermissionError):permissions.require(root/'link')
            plan=plan_reads({'image':str(path)},permissions);self.assertTrue(plan.check(permissions))
            path.write_text('changed contents')
            with self.assertRaises(PermissionError):plan.check(permissions)
