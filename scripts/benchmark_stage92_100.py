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

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(92,101),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]()
    report={'schema_version':1,'stage':args.stage,'scope':'controlled generated engineering experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
