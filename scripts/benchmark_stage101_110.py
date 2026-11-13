#!/usr/bin/env python3
"""Generated experiments for versioned recognition; no real-application accuracy."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.core.storage import atomic_json


def stage101():
    from seye.recognition.pipeline import FeaturePipeline
    image=Image.new('RGB',(80,60),'black');ImageDraw.Draw(image).rectangle((10,10,49,39),fill='white')
    r=FeaturePipeline().extract(image,['geometry'])
    return {'cases':1,'dimension':len(r['features']),'edge_density':r['features'][2],'passed':len(r['features'])==12 and r['features'][2]>0}

def stage102():
    from seye.recognition.pipeline import FeaturePipeline
    r=FeaturePipeline().extract(Image.new('RGB',(40,30),'red'),['appearance'])
    return {'cases':1,'dimension':len(r['features']),'red_high_bin_mass':r['features'][3],'flat_gradients':r['features'][12:14],'passed':len(r['features'])==30 and r['features'][3]==1 and r['features'][12:14]==[0,0]}

def stage103():
    from seye.recognition.pipeline import FeaturePipeline
    from seye.recognition.similarity import compare
    p=FeaturePipeline();a=p.extract(Image.new('RGB',(30,20),'red'),['appearance']);b=p.extract(Image.new('RGB',(30,20),'blue'),['appearance'])
    same=compare(a,a)['distance'];different=compare(a,b)['distance']
    return {'cases':2,'same_distance':same,'different_distance':different,'passed':same==0 and different>0}

def numeric_packet(value):
    from seye.core.storage import checksum
    schema={'version':'seye-feature-pipeline-v1','components':[{'name':'scalar','version':'numeric-fixture-v1','dimension':1,'offset':0}],'dimension':1}
    return {'schema':schema,'schema_sha256':checksum(schema),'features':[value]}

def numeric_row(identifier,value,label):
    from seye.core.storage import checksum
    return {'id':identifier,'group':identifier,'label':label,'packet':numeric_packet(value),'content_sha256':checksum({'numeric_fixture':value,'capture':identifier}),'source_kind':'numeric_fixture'}

def numeric_data():return [numeric_row('ta',0,'a'),numeric_row('tb',1,'b')],[numeric_row('va',.01,'a'),numeric_row('vb',1.01,'b')]

def stage104():
    from seye.learning.packet_prototypes import fit,nearest
    train,val=numeric_data();model=fit(train,val);labels=[nearest(model,row['packet'])[0]['label'] for row in val]
    return {'cases':2,'scope':'numeric algorithm fixture, not photographs','labels':labels,'passed':labels==['a','b']}

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(101,111),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]();report={'schema_version':1,'stage':args.stage,'scope':'controlled generated experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
