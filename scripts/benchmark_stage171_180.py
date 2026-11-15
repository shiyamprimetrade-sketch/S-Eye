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


def stage173():
    from seye.local.workspace import ingest
    from seye.local.reports import build_report
    from seye.core.storage import read_json
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);ingest([fixture(root)],root/'workspace',root);build_report(root/'workspace',root/'report',root)
        report=read_json(root/'report'/'report.json');status=report['items'][0]['decision']['status']
        exists=(root/'report'/'report.html').is_file()
    return {'decision_status':status,'offline_html_created':exists,'semantic_recognition_validated':False,
            'passed':status=='not_requested' and exists and not report['semantic_recognition_validated']}


def stage174():
    from seye.memory.store import Memory
    from seye.local.memory_browser import page
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);path=root/'memory.sqlite3';memory=Memory(path)
        memory.put_many([{'schema_version':1,'features':None,'provenance':{'kind':'generated_fixture','index':i}} for i in range(5)]);memory.close()
        first=page(path,root,limit=2);second=page(path,root,first['next_after'],2,first['inventory_sha256']);last=page(path,root,second['next_after'],2,first['inventory_sha256'])
        sequences=[r['sequence'] for p in (first,second,last) for r in p['items']]
    return {'paged_sequences':sequences,'last_next_after':last['next_after'],'passed':sequences==[1,2,3,4,5] and last['next_after'] is None}


def stage175():
    from seye.local.workspace import ingest,open_workspace
    from seye.local.annotation_editor import build_editor,new_draft,validate_draft
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);ingest([fixture(root)],root/'workspace',root);_,data,digest=open_workspace(root/'workspace',root)
        draft=new_draft(data,digest);draft['images'][0]['instances']=[{'id':'box-1','class':'quadrilateral','box':[15,20,51,56]}]
        result=validate_draft(draft,data,digest);build_editor(root/'workspace',root/'editor',root,draft)
        exists=(root/'editor'/'annotate.html').is_file()
    return {'draft_images':result['images'],'draft_boxes':result['instances'],'unscored':result['unscored'],
            'offline_editor_created':exists,'passed':exists and result['instances']==1 and result['unscored']}


def stage176():
    from seye.local.workspace import ingest
    from seye.local.reports import build_report
    from seye.local.comparison import load_report,compare
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);ingest([fixture(root,i) for i in (0,4)],root/'workspace',root)
        build_report(root/'workspace',root/'first',root);build_report(root/'workspace',root/'second',root)
        result=compare(load_report(root/'first'/'report.json',root),load_report(root/'second'/'report.json',root))
    return {'comparable_slots':result['comparable_slots'],'changed_decisions':result['changed_decisions'],'accuracy_change':result['accuracy_change'],
            'passed':result['comparable_slots']==2 and result['changed_decisions']==0 and result['accuracy_change'] is None}


def stage177():
    from seye.local.profiles import migrate,difference
    from seye.core.configuration import load_config
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);old=root/'old.json';new=root/'new.json'
        atomic_json(old,{'schema_version':0,'allowed_directory':str(root),'allow_write':False,'allow_memory':True});before=old.read_bytes()
        receipt=migrate(old,new,root);delta=difference(load_config(old),load_config(new))
        unchanged=old.read_bytes()==before
    return {'original_unchanged':unchanged,'enabled_capabilities':delta['enabled_capabilities'],'added_write_roots':delta['added_write_roots'],
            'in_place':receipt['in_place'],'passed':unchanged and not delta['enabled_capabilities'] and not delta['added_write_roots']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',required=True,type=int,choices=range(171,181));parser.add_argument('--output',required=True)
    args=parser.parse_args();result=globals()[f'stage{args.stage}']();atomic_json(args.output,result,overwrite=True);print(json.dumps(result,sort_keys=True))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
