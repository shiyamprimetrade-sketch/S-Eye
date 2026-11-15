#!/usr/bin/env python3
"""Controlled integration experiments; no main-S deployment or expert-vision claims."""
import argparse,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.core.storage import atomic_json


def fixture(root,index=0):
    image=Image.new('RGB',(120,90),'white');ImageDraw.Draw(image).rectangle((10+index,10,35+index,35),fill='black')
    path=Path(root)/f'view{index}.png';image.save(path);return path


def stage161():
    from seye.integration.contracts import validate_request,describe
    accepted=0;rejected=0
    for action,fields in describe()['actions'].items():
        r=dict(schema_version=1,request_id=action,action=action,**{name:'fixture' for name in fields['required']})
        validate_request(r,True);accepted+=1
        try:validate_request(dict(r,arbitrary_command='not allowed'),True)
        except ValueError:rejected+=1
    return {'structural_contracts_checked':accepted,'unknown_field_requests_rejected':rejected,
            'scope':'structural contract checks, not successful execution of every action','passed':accepted==rejected and accepted>=39}


def stage162():
    from seye.api import Client,Permissions
    from seye.integration.memory_adapter import MemoryAdapter
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);image=fixture(root);client=Client(Permissions((root,),(root,),memory=True),isolated=False,strict=True)
        adapter=MemoryAdapter(client,str(root/'memory.sqlite3'),True);saved=adapter.store_image(image,'store')
        read=adapter.observation(saved['result']['observation_id'],'read');adapter.build_index('index');query=adapter.query_image(image,'query')
        same=read['result']['identity']['source_sha256']==saved['result']['source']['sha256']
    return {'source_identity_roundtrip':same,'same_source_query_distance':query['result']['matches'][0]['distance'],
            'semantic_identity_proven':False,'passed':same and query['result']['matches'][0]['distance']==0}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',required=True,type=int,choices=range(161,171));parser.add_argument('--output',required=True)
    args=parser.parse_args();result=globals()[f'stage{args.stage}']();atomic_json(args.output,result,overwrite=True);print(json.dumps(result,sort_keys=True))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
