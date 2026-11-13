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

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(92,101),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]()
    report={'schema_version':1,'stage':args.stage,'scope':'controlled generated engineering experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
