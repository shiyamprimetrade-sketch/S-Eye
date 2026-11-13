#!/usr/bin/env python3
"""Stage 88 unlabelled photo stress experiment; no recognition-accuracy claims."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from generalization import VARIANTS, EXTRA_VARIANTS, transform
from seye.core.probes import validate_manifest
from seye.core.storage import atomic_json
from seye.detection.analysis import analyze
from seye.image.ingestion import load_image


def run(manifest):
    manifest=Path(manifest).resolve();data=validate_manifest(manifest)
    if any(r['source_kind']!='photograph' for r in data['images']):raise ValueError('Photographs required')
    results=[]
    with tempfile.TemporaryDirectory() as directory:
        for row in data['images']:
            source=manifest.parent/row['path'];image,_=load_image(source)
            for variant in VARIANTS+EXTRA_VARIANTS:
                candidate=source
                if variant!='original':
                    candidate=Path(directory)/'variant.png';transform(image,variant).save(candidate)
                for mode in ('baseline','adaptive'):
                    record={'id':row['id'],'source_sha256':row['sha256'],'variant':variant,'mode':mode}
                    try:
                        report,_=analyze(candidate,mode)
                        record.update(success=True,proposals=len(report['objects']),classes=dict(Counter(o['class'] for o in report['objects'])))
                    except (ValueError,OSError) as error:record.update(success=False,error=str(error))
                    results.append(record)
            if hashlib.sha256(source.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Original changed')
    return {'stage':88,'experiment':'unlabelled_photograph_stress','source_count':len(data['images']),
            'variants':list(VARIANTS+EXTRA_VARIANTS),'attempted_runs':len(results),'successful_runs':sum(r['success'] for r in results),
            'recognition_accuracy':None,'representative_generalization_validated':False,'original_bytes_preserved':True,
            'physical_capture_conditions':data.get('physical_capture_conditions', 'not measured; photographs show different views/scenes, not a controlled same-object sweep'),
            'limitations':['Generated perturbations are correlated, not additional photographs.','No reviewed shape labels or boxes; proposal counts are not recognized object counts.','Grid overlays may occlude foreground.','Projective warps do not prove physical viewpoint invariance.'],
            'results':results}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report=run(args.manifest);atomic_json(args.output,report)
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
