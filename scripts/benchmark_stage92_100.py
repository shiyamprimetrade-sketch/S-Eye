#!/usr/bin/env python3
"""Reproducible bounded engineering experiments, not representative UI accuracy."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.core.storage import atomic_json


def stage92():
    from seye.interface.boundaries import contours
    image=Image.new('L',(12,12));d=ImageDraw.Draw(image);d.rectangle((1,1,9,9),fill=255);d.rectangle((3,3,6,6),fill=0)
    r=contours(image)
    return {'cases':1,'loops':len(r['loops']),'holes':sum(x['role']=='hole' for x in r['loops']),
            'net_area':r['net_area'],'expected_area':65,'passed':r['net_area']==65 and len(r['loops'])==2}

def stage93():
    from benchmark_stage91 import fixtures
    from seye.interface.regions import propose_regions
    from seye.interface.grouping import pair_boundaries
    from seye.detection.metrics import detection_metrics
    totals={'tp':0,'fp':0,'fn':0}
    for metadata,image in fixtures():
        regions=pair_boundaries(propose_regions(image)['regions'])['regions']
        metrics=detection_metrics(metadata['expected'],regions)
        for key in totals:totals[key]+=metrics[key]
    return {'cases':33,'baseline':{'tp':25,'fp':8,'fn':12},'paired':totals,'passed':totals=={'tp':25,'fp':0,'fn':12}}

def stage94():
    from seye.interface.masks import split_projection
    image=Image.new('L',(70,40));d=ImageDraw.Draw(image)
    d.rectangle((10,10,24,29),fill=255);d.rectangle((40,10,54,29),fill=255);d.line((25,20,39,20),fill=255)
    r=split_projection(image)
    return {'cases':1,'parts':len(r['parts']),'removed_bridge_pixels':r['discarded_pixels'],'passed':len(r['parts'])==2 and r['discarded_pixels']==15}

def stage95():
    from seye.interface.masks import remove_specks
    image=Image.new('L',(30,20));d=ImageDraw.Draw(image);d.rectangle((5,5,14,14),fill=255)
    image.putpixel((1,1),255);image.putpixel((25,17),255)
    r=remove_specks(image)
    return {'cases':1,'retained_pixels':r['mask'].histogram()[255],'removed_pixels':r['removed_pixels'],'passed':r['removed_pixels']==2 and r['mask'].histogram()[255]==100}

def stage96():
    from seye.interface.masks import repair_gaps
    image=Image.new('L',(25,12));ImageDraw.Draw(image).line((3,5,20,5),fill=255);image.putpixel((10,5),0)
    r=repair_gaps(image)
    return {'cases':1,'introduced_pixels':r['introduced_pixels'],'retained_pixels':r['mask'].histogram()[255],'passed':r['introduced_pixels']==1 and r['mask'].histogram()[255]==18}

def stage97():
    from seye.interface.localization import localize,decode_runs
    from seye.interface.regions import edge_mask
    from seye.detection.metrics import mask_iou
    image=Image.new('RGB',(100,70),'black');ImageDraw.Draw(image).rectangle((20,10,59,39),fill='white')
    r=localize(image);m=r['regions'][0]['mask'];score=mask_iou(decode_runs(m['source_size'],m['runs']),edge_mask(image))
    return {'cases':1,'regions':len(r['regions']),'observed_stroke_mask_iou':score,'passed':score==1 and len(r['regions'])==1}

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(92,101),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]()
    report={'schema_version':1,'stage':args.stage,'scope':'controlled generated engineering experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
