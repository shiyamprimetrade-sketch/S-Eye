#!/usr/bin/env python3
"""Verify the installed Python client from a separate working directory."""
import json,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw

with tempfile.TemporaryDirectory(prefix='seye_python_api_') as directory:
    root=Path(directory);path=root/'view.png';image=Image.new('RGB',(100,80),'white')
    ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(path)
    code='''import json,sys
from seye.api import Client,Permissions,capabilities
from pathlib import Path

def main():
    root=Path(sys.argv[1]);image=str(root/'view.png')
    client=Client(Permissions(read_roots=(root,)),timeout=20)
    result=client.call('observe_interface','installed-python',image=image,region_proposals=True)
    assert result['success'],result
    batch=client.call('extract_feature_batch','installed-packets',images=[image]*3,components=['shape'])
    assert batch['success'] and batch['result']['cache']['hits']==2,batch
    denied=Client().call('observe_interface','denied',image=image)
    assert not denied['success'] and denied['error']['type']=='PermissionError',denied
    print(json.dumps({'installed_python_api_passed':True,'spawned_worker_passed':True,'default_denial_passed':True,'packet_cache_hits':2,'api_version':capabilities()['python_api_version'],'executed_outside_checkout':True}))

if __name__=='__main__':main()
'''
    completed=subprocess.run([sys.executable,'-c',code,str(root)],cwd=root,capture_output=True,text=True,timeout=70)
    if completed.returncode:raise SystemExit(completed.stdout+completed.stderr)
    print(completed.stdout.strip())
