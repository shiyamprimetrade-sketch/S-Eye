#!/usr/bin/env python3
"""Generated scene/video engineering experiments, not representative UI understanding."""
import argparse,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.core.storage import atomic_json


def view(boxes,size=(100,80)):
    return {'source_size':list(size) if size else None,'objects':[{'class':'interface_region','box':b} for b in boxes]}


def stage131():
    from seye.scenes.spatial import relationships
    actual=[relationships(view([[0,0,30,30],b]))['relations'][0]['topology'] for b in ([10,10,20,20],[25,25,50,50],[30,0,50,30],[40,0,60,20])]
    return {'cases':4,'topologies':actual,'passed':actual==['first_contains_second','overlap','touching','disjoint']}

def stage132():
    from seye.scenes.spatial import relative_positions
    a=relative_positions(view([[10,10,30,30],[60,40,80,60]]));b=relative_positions(view([[20,20,60,60],[120,80,160,120]],(200,160)))
    same=a['objects']==b['objects'] and a['offsets']==b['offsets']
    return {'cases':2,'normalized_geometry_identical':same,'passed':same}

def stage133():
    from seye.scenes.grouping import aligned_groups
    r=aligned_groups(view([[5,10,20,30],[25,10,40,30],[45,10,60,30],[70,50,90,70]]),maximum_gap=8)
    return {'cases':1,'groups':r['groups'],'links':len(r['links']),'passed':r['groups']==[[0,1,2],[3]] and len(r['links'])==2}

def stage134():
    from seye.scenes.comparison import compare_layout
    a=view([[10,10,30,30]]);b=view([[20,20,60,60]],(200,160));strict=compare_layout(a,b);normalized=compare_layout(a,b,normalize=True)
    return {'cases':2,'strict_abstention':not strict['comparable'],'explicit_normalized_similarity':normalized['geometric_similarity'],'passed':not strict['comparable'] and normalized['geometric_similarity']==1}

def stage135():
    from seye.scenes.changes import changes
    a=view([[10,10,50,40]]);b=view([[18,14,58,44]]);raw=changes(a,b);registered=changes(a,b,registration={'dx':8,'dy':4})
    return {'cases':2,'unregistered_event':raw['events'][0]['kind'],'caller_registered_event':registered['events'][0]['kind'],'passed':raw['events'][0]['kind']=='moved' and registered['events'][0]['kind']=='stable'}

def stage136():
    from seye.scenes.absence import missing_evidence
    a=view([[10,10,30,30]]);r=missing_evidence(a,[view([]),view([]),view([])]);covered=missing_evidence(a,[view([[0,0,100,80]]),view([[0,0,100,80]])])
    return {'cases':2,'persistent_nonobservation_events':len(r['events']),'cover_events':len(covered['events']),'passed':len(r['events'])==1 and not r['events'][0]['semantic_removal_proven'] and not covered['events']}

def stage137():
    from seye.scenes.description import describe
    r=describe(view([[0,0,30,30],[10,10,20,20]]))
    return {'cases':1,'facts':len(r['facts']),'semantic_description':r['semantic_description'],'passed':len(r['facts'])==2 and r['facts'][1]['evidence_ref']=='/relations/0' and r['semantic_description'] is None}

def stage138():
    from seye.scenes.uncertainty import assess
    value=view([[10,10,30,30]]);value.update(complete=False,source_sha256='a'*64);r=assess(value,{'comparable':True,'ambiguous_correspondence':True})
    return {'cases':1,'state':r['state'],'flags':r['flags'],'action_authorized':r['automatic_action_authorized'],'passed':r['state']=='partial_geometry' and 'correspondence_ambiguous' in r['flags'] and not r['automatic_action_authorized']}

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(131,141),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]();report={'schema_version':1,'stage':args.stage,'scope':'controlled generated scene/video experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
