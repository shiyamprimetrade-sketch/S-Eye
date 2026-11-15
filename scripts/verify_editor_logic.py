#!/usr/bin/env python3
"""Run editor coordinate/download logic with Node test doubles, not a browser."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from seye.local.annotation_editor import EDITOR_SCRIPT,CLASSES


def run():
    node=shutil.which('node')
    if node is None:raise ValueError('Development-only Node executable required for editor logic check')
    initial={'format':'seye-annotation-draft-v1','schema_version':1,'workspace_sha256':'a'*64,'template_unscored':True,
             'images':[{'id':'image-0001','path':'images/0001.png','sha256':'b'*64,'source_size':[500,300],
                        'source_kind':'synthetic','annotation_status':'draft','annotation_origin':'caller_drawn','capture_group':'unassigned','instances':[]}]}
    with tempfile.TemporaryDirectory(prefix='seye_editor_logic_') as directory:
        path=Path(directory)/'input.json';path.write_text(json.dumps({'script':EDITOR_SCRIPT,'initial':initial,'labels':CLASSES}))
        completed=subprocess.run([node,str(ROOT/'scripts'/'check_annotation_logic.js'),str(path)],capture_output=True,text=True,timeout=20)
        if completed.returncode:raise ValueError(completed.stdout+completed.stderr)
        return json.loads(completed.stdout)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    result=run();Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
