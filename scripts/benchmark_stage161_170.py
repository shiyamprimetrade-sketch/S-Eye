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


def stage163():
    from seye.api import Client,Permissions
    from seye.integration.tools_adapter import ToolsAdapter,manifest
    with tempfile.TemporaryDirectory() as directory:
        image=fixture(directory);adapter=ToolsAdapter(Client(Permissions((directory,)),isolated=False))
        result=adapter.invoke('seye.observe',{'image':str(image)},'tool')
        rejected=0
        for name in ('seye.click','shell','camera'):
            try:adapter.invoke(name,{},'denied')
            except ValueError:rejected+=1
    return {'registered_observation_specs':len(manifest()['tools']),'forbidden_tool_names_rejected':rejected,
            'main_s_registration':'not_deployed','passed':result['response']['success'] and rejected==3 and not result['automatic_action_authorized']}


def stage164():
    from seye.api import Permissions
    from seye.integration.boundaries import plan_reads
    from seye.integration.tools_adapter import manifest
    with tempfile.TemporaryDirectory() as directory:
        image=fixture(directory);permissions=Permissions((directory,));plan=plan_reads({'image':str(image)},permissions)
        unchanged=plan.check(permissions);image.write_bytes(b'changed')
        try:plan.check(permissions)
        except PermissionError:detected=True
        else:detected=False
    return {'unchanged_source_passed':unchanged,'changed_source_detected':detected,'live_camera_enabled':manifest()['live_camera_enabled'],
            'scope':'explicit grants and ordinary replacement checks; not a native sandbox or race-free open guarantee',
            'passed':unchanged and detected and not manifest()['live_camera_enabled']}


def stage165():
    import hashlib
    from seye.api import Client,Permissions
    with tempfile.TemporaryDirectory() as directory:
        image=fixture(directory);digest=hashlib.sha256(image.read_bytes()).hexdigest()
        client=Client(Permissions((directory,)),isolated=False,strict=True)
        good=client.call('image_observe','bound',image=str(image),expected_source_sha256=digest)
        bad=client.call('image_observe','wrong',image=str(image),expected_source_sha256='a'*64)
    return {'source_bound':good['result']['identity']['source_sha256']==digest,'wrong_source_refused':not bad['success'],
            'passed':good['success'] and not bad['success'] and not good['result']['automatic_action_authorized']}


def stage166():
    from seye.api import Client,Permissions
    from seye.integration.memory_adapter import MemoryAdapter
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);image=fixture(root);client=Client(Permissions((root,),(root,),memory=True),isolated=False,strict=True)
        adapter=MemoryAdapter(client,str(root/'memory.sqlite3'),True)
        adapter.store_image(image,'one');adapter.build_index('index-one')
        excluded=adapter.find(image,'excluded',0);unique=adapter.find(image,'unique',0,include_self=True)
        adapter.store_image(image,'two');adapter.build_index('index-two');tie=adapter.find(image,'tie',0,include_self=True)
        statuses=[r['result']['status'] for r in (excluded,unique,tie)]
    return {'controlled_statuses':statuses,'scope':'same generated image and duplicate stored observations, not real-object recognition',
            'passed':statuses==['no_match','feature_candidate','ambiguous']}


def stage167():
    from seye.integration.questions import ask
    with tempfile.TemporaryDirectory() as directory:
        image=fixture(directory);count=ask(image,'count_proposed_regions');boxes=ask(image,'list_region_boxes')
        unchanged=ask(image,'changed_pixel_fraction',image);unsupported=ask(image,'read the code')
    return {'geometric_count':count['answer'],'box_count_agrees':count['answer']==len(boxes['answer']),
            'unchanged_fraction':unchanged['answer'],'unsupported_answer':unsupported['answer'],
            'passed':count['answer']==len(boxes['answer']) and unchanged['answer']==0 and unsupported['answer'] is None}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',required=True,type=int,choices=range(161,171));parser.add_argument('--output',required=True)
    args=parser.parse_args();result=globals()[f'stage{args.stage}']();atomic_json(args.output,result,overwrite=True);print(json.dumps(result,sort_keys=True))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
