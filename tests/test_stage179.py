import unittest,tempfile,io,json
from pathlib import Path
from contextlib import redirect_stdout
from PIL import Image,ImageDraw
from seye.local.cli import main

class LocalWorkflowUsabilityTests(unittest.TestCase):
    def test_fresh_local_ingest_report_annotate_validate_and_compare_flow(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'image.png';image=Image.new('RGB',(100,80),'white');ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(source)
            commands=[['ingest','--images',str(source),'--output',str(root/'workspace')],
                      ['report','--workspace',str(root/'workspace'),'--output',str(root/'report')],
                      ['annotate','--workspace',str(root/'workspace'),'--output',str(root/'editor')],
                      ['validate-draft','--workspace',str(root/'workspace'),'--draft',str(root/'editor'/'draft.json')],
                      ['compare','--left',str(root/'report'/'report.json'),'--right',str(root/'report'/'report.json'),'--output',str(root/'compare')]]
            for args in commands:
                output=io.StringIO()
                with redirect_stdout(output):code=main(['--root',str(root),*args])
                self.assertEqual(code,0);self.assertIsInstance(json.loads(output.getvalue()),dict)
            self.assertTrue((root/'editor'/'annotate.html').exists())

    def test_cli_rejects_existing_output_without_changing_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'image.png';Image.new('RGB',(50,40),'white').save(source);before=source.read_bytes()
            with redirect_stdout(io.StringIO()):main(['--root',str(root),'ingest','--images',str(source),'--output',str(root/'workspace')])
            with self.assertRaises(SystemExit):main(['--root',str(root),'ingest','--images',str(source),'--output',str(root/'workspace')])
            self.assertEqual(source.read_bytes(),before)
