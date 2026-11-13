#!/usr/bin/env python3
"""Compare frozen pixel matching to independent local-contrast/scale matching."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image, ImageDraw
from benchmark_stage89 import fixtures
from seye.interface.observer import observe
from seye.interface.evaluation import summarize
from seye.core.storage import atomic_json,checksum


def heldout():
    for family in ('plus','chevron'):
        def draw_icon(theme):
            image=Image.new('RGB',(24,16),'navy' if theme=='dark' else 'white');d=ImageDraw.Draw(image)
            color='yellow' if theme=='dark' else 'black'
            if family=='plus':
                d.rectangle((10,2,13,13),fill=color);d.rectangle((4,6,19,9),fill=color)
            else:d.line([(6,2),(16,8),(6,13)],fill=color,width=3)
            return image
        reference=draw_icon('dark')
        for theme in ('dark','light'):
            for scale in (.75,1.25):
                size=(round(24*scale),round(16*scale));control=draw_icon(theme).resize(size,Image.Resampling.NEAREST)
                for state in ('single','absent','duplicate','occluded'):
                    background=(70,70,70) if theme=='dark' else (160,160,160)
                    before=Image.new('RGB',(208,128),background);after=before.copy()
                    locations=[] if state=='absent' else [(52,20)]
                    if state=='duplicate':locations.append((136,60))
                    boxes=[]
                    for x,y in locations:after.paste(control,(x,y));boxes.append([x,y,x+size[0],y+size[1]])
                    if state=='occluded':ImageDraw.Draw(after).rectangle((52,20,52+size[0]//2-1,20+size[1]-1),fill=background)
                    pixels=len(locations)*size[0]*size[1]
                    if state=='occluded':pixels-=size[0]//2*size[1]
                    expected='visual_candidate' if state=='single' else 'ambiguous' if state=='duplicate' else 'not_found'
                    yield {'id':f'heldout-{family}-{theme}-{scale}-{state}','family':family,'theme':theme,'scale':scale,'state':state,
                           'expected_status':expected,'expected_boxes':boxes if expected!='not_found' else [],
                           'expected_change':{'signal':'pixels_changed' if pixels else 'pixels_unchanged','changed_pixels':pixels}},before,after,reference


def pixel_digest(image):
    rgb=image.convert('RGB')
    return hashlib.sha256(f'RGB:{rgb.width}:{rgb.height}:'.encode()+rgb.tobytes()).hexdigest()


def frozen_equivalent(actual, frozen, pixel_identities):
    # Encoded PNG bytes can differ across platform zlib builds. Keep their hashes
    # as provenance, but require canonical RGB pixels and all semantic results.
    encoded={'source_sha256','previous_sha256','template_sha256'}
    pixels={'source_pixel_sha256','previous_pixel_sha256','template_pixel_sha256'}
    if actual['summary']!=frozen['summary']:return False
    first=[{k:v for k,v in row.items() if k not in encoded|pixels} for row in actual['cases']]
    second=[{k:v for k,v in row.items() if k not in encoded} for row in frozen['cases']]
    if first!=second:return False
    observed={row['id']:{key:row[key] for key in pixels} for row in actual['cases']}
    return observed==pixel_identities


def run():
    suites={'frozen_stage89':list(fixtures()),'heldout_designs':list(heldout())}
    protocol={'threshold':1,'stride':4,'scales':[.75,1,1.25,1.5,2],
              'heldout_designs':['plus','chevron'],'heldout_scales':[.75,1.25],
              'selection':'Fixed before first execution; no training, threshold search or model selection',
              'scope':'generated glyphs only; held-out designs still share renderer and are not external application validation'}
    report={'schema_version':1,'stage':90,'protocol':protocol,'protocol_sha256':checksum(protocol),'suites':{}}
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        for suite,items in suites.items():
            cases={mode:[] for mode in ('pixel','contrast')}
            for metadata,before,after,template in items:
                before.save(root/'before.png');after.save(root/'after.png');templates=[]
                if template is not None:
                    template.save(root/'template.png');templates=[{'name':metadata['family'],'path':root/'template.png'}]
                provenance={'source_pixel_sha256':pixel_digest(after),
                            'previous_pixel_sha256':pixel_digest(before),
                            'template_pixel_sha256':pixel_digest(template) if template is not None else None,
                            'source_sha256':hashlib.sha256((root/'after.png').read_bytes()).hexdigest(),
                            'previous_sha256':hashlib.sha256((root/'before.png').read_bytes()).hexdigest(),
                            'template_sha256':hashlib.sha256((root/'template.png').read_bytes()).hexdigest() if templates else None}
                for mode in cases:
                    row=dict(metadata,**provenance)
                    try:
                        result=observe(root/'after.png',root/'before.png',templates,stride=4,min_similarity=1,matcher=mode)
                        match=result['elements'][0] if templates else {'status':'not_found','candidate':None}
                        row.update(observed_status=match['status'],candidate=match['candidate'],change=result['change'])
                    except (ValueError,OSError) as error:row.update(observed_status='execution_error',candidate=None,error=str(error))
                    cases[mode].append(row)
            report['suites'][suite]={mode:{'summary':summarize(rows),'cases':rows} for mode,rows in cases.items()}
    frozen=json.loads((ROOT/'benchmarks/stage89_interface_conditions.json').read_text())
    pixels=json.loads((ROOT/'benchmarks/stage89_pixel_identities.json').read_text())['images']
    report['acceptance']={'frozen_pixel_baseline_preserved':frozen_equivalent(report['suites']['frozen_stage89']['pixel'],frozen,pixels)}
    for suite,methods in report['suites'].items():
        result=methods['contrast']['summary']
        report['acceptance'][suite+'_contrast_contract']=(result['completed_cases']==result['requested_cases'] and
            result['status_matches']==result['requested_cases'] and result['localization']['false_negatives']==0 and
            result['localization']['false_positives']==0 and result['ambiguity_safety']['unsafe_single_choices']==0 and
            result['change_oracle']['exact_matches']==result['requested_cases'])
    report['engineering_acceptance_passed']=all(report['acceptance'].values())
    report['representative_application_accuracy']=None
    report['limitations']=['Generated controls only; no OCR, semantic understanding, real host capture or input execution.',
                          'Binary contrast loses color/texture identity and may confuse different controls.',
                          'Explicit scales, stride alignment and local contrast limits bound support.',
                          'Overlapping controls and unseen scales/themes need broader testing.']
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();report=run();atomic_json(args.output,report)
    for suite,methods in report['suites'].items():
        for method,r in methods.items():print(suite,method,json.dumps({k:v for k,v in r['summary'].items() if k in ('requested_cases','completed_cases','status_matches','localization','ambiguity_safety','change_oracle')}))
    if not report['engineering_acceptance_passed']:raise SystemExit(1)
    if any(r['summary']['execution_errors'] for methods in report['suites'].values() for r in methods.values()):raise SystemExit(1)
