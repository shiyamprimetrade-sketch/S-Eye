#!/usr/bin/env python3
"""Installed local CLI workflows from outside the checkout; generated inputs only."""
import json,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw

with tempfile.TemporaryDirectory(prefix='seye_local_smoke_') as directory:
    root=Path(directory);image=Image.new('RGB',(160,100),'white');ImageDraw.Draw(image).rectangle((15,20,50,55),fill='black');image.save(root/'capture.png')
    checked=[]
    def command(name,*fields):
        arguments=[sys.executable,'-m','seye.local.cli','--root',str(root),name,*map(str,fields)]
        result=subprocess.run(arguments,cwd=root,capture_output=True,text=True,timeout=60)
        assert result.returncode==0,(arguments,result.stdout,result.stderr)
        checked.append(name);return json.loads(result.stdout)
    command('doctor','--self-test','--require-installed')
    command('ingest','--images',root/'capture.png','--source-kind','synthetic','--output',root/'workspace')
    command('overlays','--workspace',root/'workspace','--output',root/'overlays')
    command('report','--workspace',root/'workspace','--output',root/'report')
    command('annotate','--workspace',root/'workspace','--output',root/'editor')
    valid=command('validate-draft','--workspace',root/'workspace','--draft',root/'editor'/'draft.json');assert valid['unscored']
    command('compare','--left',root/'report'/'report.json','--right',root/'report'/'report.json','--output',root/'comparison')
    command('config-init','--output',root/'profile.json');profile=command('config-inspect','--path',root/'profile.json')
    assert not profile['normalized']['write_roots'] and not profile['normalized']['memory']
    old=root/'old.json';old.write_text(json.dumps({'schema_version':0,'allowed_directory':str(root),'allow_write':False,'allow_memory':False}))
    command('config-migrate','--source',old,'--output',root/'migrated.json')
    code='''from seye.memory.store import Memory
from pathlib import Path
import sys
m=Memory(Path(sys.argv[1])/'memory.sqlite3');m.put_many([{'schema_version':1,'features':None,'provenance':{'kind':'generated_local_smoke','index':i}} for i in range(3)]);m.close()'''
    subprocess.run([sys.executable,'-c',code,str(root)],cwd=root,check=True,capture_output=True,text=True,timeout=30)
    command('memory','--memory',root/'memory.sqlite3','--output',root/'browser','--limit','2')
    assert (root/'editor'/'annotate.html').is_file() and (root/'browser'/'memory.html').is_file()
    print(json.dumps({'installed_local_cli_passed':True,'executed_outside_checkout':True,'checked_commands':checked,
                      'draft_unscored':True,'independent_human_usability_validated':False,'v1_release':False},sort_keys=True))
