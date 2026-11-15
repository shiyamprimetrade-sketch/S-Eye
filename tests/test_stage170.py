import unittest,tempfile,subprocess,sys,json,os
from pathlib import Path
from PIL import Image

class WorkflowContractCLITests(unittest.TestCase):
    def command(self,*args):
        env=dict(os.environ);env['PYTHONPATH']=str(Path(__file__).resolve().parents[1]/'src')
        return subprocess.run([sys.executable,'-m','seye.api.workflow',*args],capture_output=True,text=True,env=env,timeout=25)

    def test_describe_without_grants_and_strict_installed_style_workflow(self):
        described=self.command('--describe-contract');self.assertEqual(described.returncode,0,described.stderr)
        self.assertIn('ask_observation',json.loads(described.stdout)['actions'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);image=root/'image.png';Image.new('RGB',(40,30),'white').save(image)
            request=root/'request.json';output=root/'output.json'
            request.write_text(json.dumps({'schema_version':1,'request_id':'cli','action':'image_observe','image':str(image)}))
            result=self.command('--request',str(request),'--output',str(output),'--read-root',str(root),'--write-root',str(root),'--strict')
            self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(json.loads(output.read_text())['success'])

    def test_duplicate_and_unknown_fields_fail_without_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);request=root/'bad.json';output=root/'output.json'
            for raw in ('{"schema_version":1,"schema_version":2}',json.dumps({'schema_version':1,'request_id':'r','action':'analyze','image':'x','command':'anything'})):
                request.write_text(raw)
                result=self.command('--request',str(request),'--output',str(output),'--read-root',str(root),'--write-root',str(root),'--strict')
                self.assertEqual(result.returncode,2);self.assertFalse(output.exists())
