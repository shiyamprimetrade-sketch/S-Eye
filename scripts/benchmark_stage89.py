#!/usr/bin/env python3
"""Generated screenshot condition matrix with automatic geometric ground truth."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image, ImageDraw
import PIL
from seye.interface.observer import observe
from seye.interface.evaluation import summarize
from seye.core.storage import atomic_json, checksum

FAMILIES=('run','stop','menu')


def icon(family, theme='dark'):
    image=Image.new('RGB',(24,16),'navy' if theme=='dark' else 'white')
    draw=ImageDraw.Draw(image);color='yellow' if theme=='dark' else 'black'
    if family=='run':draw.polygon([(6,3),(18,8),(6,13)],fill=color)
    elif family=='stop':draw.rectangle((6,3,17,12),fill=color)
    elif family=='menu':
        for y in (3,7,11):draw.line((4,y,19,y),fill=color,width=2)
    else:raise ValueError('Unknown generated family')
    return image


def fixtures():
    """Render metadata and pixel bytes deterministically without reading predictions."""
    for family in FAMILIES:
        reference=icon(family)
        for theme in ('dark','light'):
            for scale in (1,1.5,2):
                size=(int(24*scale),int(16*scale))
                control=icon(family,theme).resize(size,Image.Resampling.NEAREST)
                for state in ('single','absent','duplicate','occluded'):
                    previous=Image.new('RGB',(208,128),(30,30,30) if theme=='dark' else (220,220,220))
                    draw=ImageDraw.Draw(previous)
                    toolbar=(70,70,70) if theme=='dark' else (160,160,160)
                    draw.rectangle((0,0,207,47),fill=toolbar)
                    for y in range(60,120,12):draw.line((40,y,130,y),fill=(100,160,110),width=2)
                    current=previous.copy();locations=[] if state=='absent' else [(40,12)]
                    if state=='duplicate':locations.append((136,12))
                    boxes=[]
                    for x,y in locations:
                        current.paste(control,(x,y));boxes.append([x,y,x+size[0],y+size[1]])
                    if state=='occluded':
                        ImageDraw.Draw(current).rectangle((40,12,40+size[0]//2-1,12+size[1]-1),fill=toolbar)
                    pixels=len(locations)*size[0]*size[1]
                    if state=='occluded':pixels//=2
                    expected='visual_candidate' if state=='single' else 'ambiguous' if state=='duplicate' else 'not_found'
                    # Occluded controls are deliberately unsupported, not fully visible targets.
                    yield {'id':f'{family}-{theme}-{scale}-{state}','family':family,'theme':theme,'scale':scale,
                           'state':state,'expected_status':expected,
                           'expected_boxes':boxes if expected!='not_found' else [],
                           'expected_change':{'signal':'pixels_changed' if pixels else 'pixels_unchanged','changed_pixels':pixels}}, previous,current,reference
    before=Image.new('RGB',(208,128),'gray')
    after=before.copy();ImageDraw.Draw(after).rectangle((40,64,41,65),fill='white')
    for state,current,signal,pixels in [('unchanged',before,'pixels_unchanged',0),('tiny_cursor',after,'pixels_changed',4),
                                        ('viewport_resize',before.resize((208,144)),'viewport_changed',None)]:
        yield {'id':state,'family':'no_template','theme':'neutral','scale':1,'state':state,'expected_status':'not_found',
               'expected_boxes':[],'expected_change':{'signal':signal,'changed_pixels':pixels}},before,current,None


def run():
    cases=[]
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        for metadata,previous,current,template in fixtures():
            previous.save(root/'previous.png');current.save(root/'current.png')
            templates=[]
            if template is not None:
                template.save(root/'template.png');templates=[{'name':metadata['family'],'path':root/'template.png'}]
            row=dict(metadata,source_sha256=hashlib.sha256((root/'current.png').read_bytes()).hexdigest(),
                     previous_sha256=hashlib.sha256((root/'previous.png').read_bytes()).hexdigest(),
                     template_sha256=hashlib.sha256((root/'template.png').read_bytes()).hexdigest() if templates else None)
            try:
                result=observe(root/'current.png',root/'previous.png',templates,stride=4,min_similarity=1)
                match=result['elements'][0] if templates else {'status':'not_found','candidate':None}
                row.update(observed_status=match['status'],candidate=match['candidate'],change=result['change'])
            except (OSError,ValueError) as error:
                row.update(observed_status='execution_error',candidate=None,error=str(error))
            cases.append(row)
    summary=summarize(cases)
    return {'schema_version':1,'stage':89,'experiment':'generated_interface_conditions',
            'oracle':'renderer metadata; no manual annotations or recognition-derived labels',
            'protocol':{'families':list(FAMILIES),'themes':['dark','light'],'scales':[1,1.5,2],
                        'states':['single','absent','duplicate','occluded'],'stride':4,'min_similarity':1,
                        'selection':'fixed complete Cartesian matrix plus three frame-change controls; no training or threshold selection',
                        'reference':'one native-size dark template per family; no theme/scale adaptation'},
            'environment':{'python':platform.python_version(),'pillow':PIL.__version__},
            'fixture_identity':checksum([{k:v for k,v in c.items() if k not in ('observed_status','candidate','change','error')} for c in cases]),
            'summary':summary,'cases':cases,
            'limitations':['Generated fixtures share render primitives and are not independent application screenshots.',
                           'Status scoring is a bounded template contract, not semantic recognition accuracy.',
                           'No positive occlusion support is claimed: occluded controls are rejection cases.',
                           'Strict fixed-scale baseline is intentionally retained; theme/scale failures remain evidence.',
                           'A small pixel change can emit a signal without meeting changed-tile box thresholds.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=run();atomic_json(args.output,report)
    print(json.dumps(report['summary'],indent=2))
    if report['summary']['execution_errors']:raise SystemExit(1)
