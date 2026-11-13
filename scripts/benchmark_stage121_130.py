#!/usr/bin/env python3
"""Bounded memory experiments, not representative visual intelligence accuracy."""
import argparse,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.core.storage import atomic_json,checksum


def stage121():
    from seye.memory.identity import pixel_identity,identify
    image=Image.new('RGB',(20,10),'red');digest=pixel_identity(image)
    r=identify({'schema_version':1,'features':None,'analysis':{'source':{'pixel_sha256':digest}},'provenance':{'source_sha256':'a'*64}})
    return {'cases':1,'pixel_identity_preserved':r['decoded_pixel_sha256']==digest,'missing_model_identity':r['model_sha256'],'passed':r['decoded_pixel_sha256']==digest and r['model_sha256'] is None}

def numeric_record(value):
    from benchmark_stage101_110 import numeric_packet
    return {'schema_version':1,'features':None,'packet':numeric_packet(value),'provenance':{'kind':'numeric_memory_fixture','source_sha256':checksum({'numeric_fixture':value})}}

def stage122():
    from seye.memory.store import Memory
    from seye.memory.packet_index import rebuild,load_tree
    with tempfile.TemporaryDirectory() as directory:
        m=Memory(Path(directory)/'m.sqlite3')
        try:
            for i in range(16):m.put(numeric_record(i/16))
            r=rebuild(m);tree=load_tree(m,numeric_record(0)['packet']['schema_sha256'])
        finally:m.close()
    return {'cases':16,'indexed_observations':r['indexed_observations'],'tree_count':tree['count'],'passed':r['indexed_observations']==16 and tree['count']==16}

def stage123():
    from seye.memory.store import Memory
    from seye.memory.packet_index import rebuild,query
    from seye.recognition.similarity import compare
    with tempfile.TemporaryDirectory() as directory:
        m=Memory(Path(directory)/'m.sqlite3');items=[]
        try:
            for i in range(64):
                row=numeric_record(i/64);items.append((m.put(row),row))
            rebuild(m);packet=numeric_record(.41)['packet'];r=query(m,packet,limit=3)
            expected=sorted(items,key=lambda item:(compare(packet,item[1]['packet'])['distance'],item[0]))[:3]
            same=[x['id'] for x in r['matches']]==[x[0] for x in expected]
        finally:m.close()
    return {'cases':64,'top3_exact':same,'distance_evaluations':r['distance_evaluations'],'exhaustive_distance_evaluations':64,'passed':same and r['distance_evaluations']<64}

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(121,131),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]();report={'schema_version':1,'stage':args.stage,'scope':'controlled generated memory experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
