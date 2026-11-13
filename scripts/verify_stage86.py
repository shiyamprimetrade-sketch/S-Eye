#!/usr/bin/env python3
"""Stage 86 acceptance: multi-image loading/identity, not recognition validation."""
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from PIL import Image
from generalization import load_manifest,digest


def verify():
    checks=[]
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);rows=[]
        for number,extension in enumerate(('png','jpg','png')):
            path=root/f'{number}.{extension}';Image.new('RGB',(32+number,24),(number*60,90,180)).save(path)
            rows.append({'id':str(number),'path':path.name,'sha256':digest(path),'source_kind':'synthetic',
                         'human_confirmed':False,'expected_classes':[],'capture_group':str(number),
                         'lighting':'generated','camera_angle':'generated','annotation_source':'acceptance generator'})
        manifest=root/'manifest.json'
        def save(items):manifest.write_text(json.dumps({'schema_version':1,'images':items}))
        before={row['path']:digest(root/row['path']) for row in rows}
        save(rows);assert len(load_manifest(manifest)['images'])==3;checks.append('three mixed JPEG/PNG sources loaded')
        assert before=={name:digest(root/name) for name in before};checks.append('input bytes unchanged')
        cases=[('duplicate identity',rows+[dict(rows[0])]),
               ('duplicate source bytes',rows+[dict(rows[0],id='copy')]),
               ('hash mismatch',[dict(rows[0],sha256='0'*64)]),
               ('path escape',[dict(rows[0],path='../outside.png')])]
        for name,items in cases:
            save(items)
            try:load_manifest(manifest)
            except ValueError:checks.append(name+' rejected')
            else:raise AssertionError(name+' accepted')
    return {'stage':86,'acceptance_scope':'multi-image loading and byte identity contract',
            'checks_passed':len(checks),'checks':checks,'engineering_acceptance_passed':True,
            'photographic_recognition_validated':False,'next_stage':87}

if __name__=='__main__':
    result=verify()
    if len(sys.argv)!=2:raise SystemExit('Usage: verify_stage86.py NEW_REPORT.json')
    path=Path(sys.argv[1])
    with path.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2))
