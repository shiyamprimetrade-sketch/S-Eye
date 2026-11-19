#!/usr/bin/env python3
"""Automatic region box oracles; no template or semantic control labels."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.interface.regions import propose_regions
from seye.detection.metrics import detection_metrics
from seye.core.storage import atomic_json,checksum


def fixtures():
    for theme in ('dark','light'):
        background=(30,30,30) if theme=='dark' else (225,225,225)
        foreground=(220,220,220) if theme=='dark' else (35,35,35)
        for scale in (1,1.5):
            for state in ('single','multiple','outlined','nested','overlap','noise','low_contrast','blank'):
                image=Image.new('RGB',(240,160),background);draw=ImageDraw.Draw(image)
                boxes=[]
                def rect(box,fill=foreground,outline=False):
                    # Oracle is specified before any observation; half-open box conversion.
                    box=[round(v*scale) for v in box]
                    if outline:draw.rectangle((box[0],box[1],box[2]-1,box[3]-1),outline=fill,width=2)
                    else:draw.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=fill)
                    boxes.append({'box':box,'class':'interface_region'})
                if state=='single':rect([20,16,60,40])
                elif state=='multiple':rect([20,16,60,40]);rect([100,64,140,88])
                elif state=='outlined':rect([20,16,70,48],outline=True)
                elif state=='nested':
                    rect([12,8,148,96],outline=True);rect([40,32,80,56])
                elif state=='overlap':rect([20,16,70,48]);rect([50,32,100,64])
                elif state=='low_contrast':rect([20,16,60,40],fill=tuple(c+5 if c<128 else c-5 for c in background))
                elif state=='noise':
                    for i in range(30):
                        x=(17*i+3)%image.width;y=(29*i+5)%image.height;draw.point((x,y),fill=foreground)
                yield {'id':f'{theme}-{scale}-{state}','theme':theme,'scale':scale,'state':state,'expected':boxes},image
    # Equal-luminance color edge, to ensure RGB evidence is not discarded by grayscale.
    image=Image.new('RGB',(240,160),(255,0,0));ImageDraw.Draw(image).rectangle((20,16,59,39),fill=(0,130,0))
    yield {'id':'chromatic-edge','theme':'chromatic','scale':1,'state':'single',
           'expected':[{'box':[20,16,60,40],'class':'interface_region'}]},image


def run():
    cases=[];groups={};totals={'tp':0,'fp':0,'fn':0};completed=0
    for metadata,image in fixtures():
        row=dict(metadata,pixel_sha256=hashlib.sha256(image.tobytes()).hexdigest(),source_size=list(image.size))
        try:
            result=propose_regions(image);score=detection_metrics(metadata['expected'],result['regions'])
            row.update(success=True,proposals=result,metrics=score);completed+=1
            for key in totals:totals[key]+=score[key]
            for field in ('theme','scale','state'):
                group=groups.setdefault(field,{}).setdefault(str(metadata[field]),{'cases':0,'tp':0,'fp':0,'fn':0})
                group['cases']+=1
                for key in totals:group[key]+=score[key]
        except (ValueError,OSError) as error:
            totals['fn']+=len(metadata['expected'])
            row.update(success=False,error=str(error),missed_due_to_execution=len(metadata['expected']))
        cases.append(row)
    return {'schema_version':1,'stage':91,'experiment':'generated_template_free_interface_regions',
            'oracle':'renderer half-open region boxes; no predictions used to label fixtures',
            'parameters':{'edge_threshold':24,'min_width':12,'min_height':8,'min_border_coverage':.75,'iou_threshold':.5},
            'case_count':len(cases),'completed_cases':completed,'execution_errors':len(cases)-completed,
            'localization':totals,'localization_accounting':'All requested targets; execution failures count as misses. Condition groups contain completed cases only.',
            'by_condition':groups,'cases':cases,
            'fixture_identity':checksum([{k:v for k,v in row.items() if k not in ('success','proposals','metrics','error')} for row in cases]),
            'representative_application_accuracy':None,
            'limitations':['Generated rectangular regions, not semantic controls or real-application validation.',
                           'Outline inner/outer boundaries may generate duplicate proposals.',
                           'Overlapping rectangles can merge or be rejected; low contrast is unsupported.',
                           'IoU scores evaluate proposed visual regions, not clickability or functional meaning.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=run();atomic_json(args.output,report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('cases','by_condition','limitations')},indent=2))
    if report['execution_errors']:raise SystemExit(1)
