#!/usr/bin/env python3
"""Installed spawned observe/store/index/find/question and strict CLI contract."""
import json,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw

with tempfile.TemporaryDirectory(prefix='seye_s_integration_') as directory:
    root=Path(directory);image=Image.new('RGB',(120,90),'white');ImageDraw.Draw(image).rectangle((10,10,35,35),fill='black');image.save(root/'screen.png')
    code='''import json,sys
from pathlib import Path
from seye.api import Client,Permissions
from seye.integration.memory_adapter import MemoryAdapter
from seye.integration.session import EyeSession

def main():
    root=Path(sys.argv[1]);client=Client(Permissions((root,),(root,),memory=True),timeout=30,strict=True)
    memory=MemoryAdapter(client,str(root/'memory.sqlite3'),writable=True)
    result=EyeSession(client,'installed-flow',memory).run(root/'screen.png',persist=True,maximum_distance=0,include_self=True)
    assert result['success'],result
    assert [s['operation'] for s in result['steps']]==['observe','store','index','find','question'],result
    assert not result['automatic_action_authorized']
    print(json.dumps({'installed_spawned_session_passed':True,'operations':len(result['steps']),'explicit_write_steps':result['successful_write_steps'],'main_s_deployment':False}))

if __name__=='__main__':main()
'''
    completed=subprocess.run([sys.executable,'-c',code,str(root)],cwd=root,capture_output=True,text=True,timeout=170)
    if completed.returncode:raise SystemExit(completed.stdout+completed.stderr)
    result=json.loads(completed.stdout)
    described=subprocess.run([sys.executable,'-m','seye.api.workflow','--describe-contract'],cwd=root,capture_output=True,text=True,timeout=30)
    assert described.returncode==0,described.stderr
    assert json.loads(described.stdout)['format']=='seye-action-contract-v1'
    request={'schema_version':1,'request_id':'installed-cli','action':'ask_observation','image':str(root/'screen.png'),'question':'count_proposed_regions'}
    path=root/'request.json';path.write_text(json.dumps(request))
    cli=subprocess.run([sys.executable,'-m','seye.api.workflow','--request',str(path),'--output',str(root/'answer.json'),
                        '--read-root',str(root),'--write-root',str(root),'--strict'],cwd=root,capture_output=True,text=True,timeout=40)
    assert cli.returncode==0,(cli.stdout,cli.stderr)
    answer=json.loads((root/'answer.json').read_text());assert answer['success'] and answer['result']['status']=='answered'
    result.update(strict_installed_cli_passed=True,describe_contract_passed=True,executed_outside_checkout=True)
    print(json.dumps(result,sort_keys=True))
