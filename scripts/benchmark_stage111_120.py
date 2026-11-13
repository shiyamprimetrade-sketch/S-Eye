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

def stage113():
    from learning_batch_data import dataset,protocol
    from seye.learning.packet_linear import fit
    d=dataset();m=fit(d['train'],d['validation'],**protocol()['sgd']);initial=m['initial_training']['cross_entropy'];final=m['history'][-1]['training']['cross_entropy']
    return {'cases':9,'initial_training_cross_entropy':initial,'final_training_cross_entropy':final,'best_epoch':m['best_epoch'],'passed':final<initial and not m['pretrained_weights_used']}

def stage114():
    import tempfile
    from learning_batch_data import dataset
    from seye.learning.packet_linear import fit,scores
    from seye.learning.training_checkpoint import save,load
    d=dataset();m=fit(d['train'],d['validation'],epochs=5)
    with tempfile.TemporaryDirectory() as directory:
        p=Path(directory)/'model.json';save(p,m);same=scores(m,d['validation'][0]['packet'])==scores(load(p),d['validation'][0]['packet'])
    return {'cases':1,'restored_scores_identical':same,'optimizer_resume_claimed':False,'passed':same}

def stage115():
    from learning_batch_data import dataset
    from seye.learning.reproducibility import reproduce
    d=dataset();r=reproduce(d['train'],d['validation'],{'epochs':8,'seed':113,'learning_rate':.2})
    return {'cases':2,'identical':r['identical'],'source_sha256':r['algorithm_source_sha256'],'model_sha256':r['first_model_sha256'],'passed':r['identical']}

def stage116():
    from learning_batch_data import dataset
    from seye.learning.packet_linear import fit
    from seye.learning.diagnostics import overfitting
    d=dataset();r=overfitting(fit(d['train'],d['validation'],epochs=20)['history'])
    return {'cases':1,'diagnostics':r,'passed':not r['test_data_used']}

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(111,121),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]();report={'schema_version':1,'stage':args.stage,'scope':'controlled generated engineering experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
