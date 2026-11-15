#!/usr/bin/env python3
"""Generated local workflow controls; not representative recognition validation."""
import argparse,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.core.storage import atomic_json


def fixture(root,index=0):
    image=Image.new('RGB',(160,100),'white');ImageDraw.Draw(image).rectangle((15+index,20,50+index,55),fill='black')
    path=Path(root)/f'capture{index}.png';image.save(path);return path


def stage171():
    from seye.local.workspace import ingest,open_workspace
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);images=[fixture(root,i) for i in (0,4,8)];receipt=ingest(images,root/'workspace',root)
        _,data,digest=open_workspace(root/'workspace',root)
    return {'snapshot_images':len(data['items']),'completion_digest_matches':digest==receipt['manifest_sha256'],
            'passed':len(data['items'])==3 and digest==receipt['manifest_sha256']}


def stage172():
    from seye.local.workspace import ingest
    from seye.local.overlays import overlay_workspace
    from seye.core.storage import read_json
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);ingest([fixture(root)],root/'workspace',root);overlay_workspace(root/'workspace',root/'overlays',root)
        row=read_json(root/'overlays'/'manifest.json')['payload']['items'][0]
        with Image.open(root/'overlays'/row['overlay']) as image:size=list(image.size)
    return {'source_size':row['source_size'],'overlay_size':size,'region_count':len(row['regions']),
            'passed':size==row['source_size'] and len(row['regions'])>=1}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',required=True,type=int,choices=range(171,181));parser.add_argument('--output',required=True)
    args=parser.parse_args();result=globals()[f'stage{args.stage}']();atomic_json(args.output,result,overwrite=True);print(json.dumps(result,sort_keys=True))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
