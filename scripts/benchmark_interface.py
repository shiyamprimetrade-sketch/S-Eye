#!/usr/bin/env python3
"""Reproducible generated UI checks; no human-expert or application accuracy claim."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image, ImageDraw, ImageEnhance
from seye.interface.observer import observe
from seye.core.storage import atomic_json


def run():
    icon=Image.new('RGB',(24,16),'navy');d=ImageDraw.Draw(icon)
    d.rectangle((2,2,21,13),outline='white',width=2);d.line((4,8,18,8),fill='yellow',width=2)
    screen=Image.new('RGB',(240,160),(30,30,30));d=ImageDraw.Draw(screen)
    d.rectangle((0,0,239,39),fill=(70,70,70));d.rectangle((0,40,47,159),fill=(45,45,45))
    for y in range(55,140,12):d.line((60,y,160,y),fill=(120,160,130),width=2)
    cases=[]
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);icon.save(root/'template.png');screen.save(root/'previous.png')
        for name,locations,expected,dim in [
            ('known_control',[(80,12)],'visual_candidate',False),
            ('translated_control',[(160,12)],'visual_candidate',False),
            ('absent_control',[],'not_found',False),
            ('duplicate_controls',[(80,12),(160,12)],'ambiguous',False),
            ('dimmed_control',[(80,12)],'not_found',True)]:
            image=screen.copy()
            for point in locations:image.paste(icon,point)
            if dim:image=ImageEnhance.Brightness(image).enhance(.4)
            image.save(root/'current.png');start=time.perf_counter()
            result=observe(root/'current.png',root/'previous.png',[{'name':'run','path':root/'template.png'}],min_similarity=1)
            found=result['elements'][0]
            cases.append({'case':name,'expected_status':expected,'observed_status':found['status'],
                          'status_matches':found['status']==expected,'candidate':found['candidate'],
                          'change':result['change'],'elapsed_seconds':time.perf_counter()-start})
        # Repeat the same rendered screenshot: expected no change, not robustness.
        unchanged=observe(root/'previous.png',root/'previous.png')['change']
    return {'schema_version':1,'experiment':'generated_interface_observation',
            'cases':cases,'status_matches':sum(c['status_matches'] for c in cases),
            'case_count':len(cases),'unchanged_control':unchanged,
            'recognition_accuracy':None,'human_expert_equivalence_validated':False,
            'limitations':['Five generated UI cases using one known template; no independent application validation.',
                           'Strict fixed-scale pixel matching rejects brightness changes by design.',
                           'No OCR, code comprehension, browser/OS capture or action execution.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=run();atomic_json(args.output,report)
    print(json.dumps({'cases':report['case_count'],'status_matches':report['status_matches']}))

    if report['status_matches'] != report['case_count']:
        raise SystemExit(1)
