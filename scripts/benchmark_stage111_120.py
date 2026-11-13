#!/usr/bin/env python3
"""Bounded generated learning experiments; stage execution is not recognition accuracy."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.core.storage import atomic_json


def stage111():
    from seye.recognition.pipeline import FeaturePipeline
    p=FeaturePipeline();vectors=[]
    for x in (5,40):
        image=Image.new('RGB',(100,70),'black');ImageDraw.Draw(image).rectangle((x,10,x+19,29),fill='white');vectors.append(p.extract(image,['shape']))
    return {'cases':2,'translation_identity':vectors[0]==vectors[1],'dimension':len(vectors[0]['features']),'passed':vectors[0]==vectors[1] and len(vectors[0]['features'])==257}

def stage112():
    from learning_batch_data import dataset
    from seye.learning.partitions import validate_partitions
    r=validate_partitions(dataset())
    return {'cases':25,'partition_counts':r['counts'],'near_duplicate_scene_independence_certified':False,'passed':r['counts']=={'train':9,'validation':6,'test':10}}

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(111,121),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]();report={'schema_version':1,'stage':args.stage,'scope':'controlled generated engineering experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
