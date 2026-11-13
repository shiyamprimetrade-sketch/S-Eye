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

# STAGE_CASES
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=range(121,131),required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=globals()['stage'+str(args.stage)]();report={'schema_version':1,'stage':args.stage,'scope':'controlled generated memory experiment','result':result,'representative_application_accuracy':None}
    atomic_json(args.output,report);print(json.dumps(report))
    if not result['passed']:raise SystemExit(1)
