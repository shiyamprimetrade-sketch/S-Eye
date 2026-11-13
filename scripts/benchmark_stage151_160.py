#!/usr/bin/env python3
"""Generated resource/latency experiments; no representative vision claims."""
import argparse,hashlib,io,json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw,ImageOps
from seye.core.storage import atomic_json


def fixture(root,index=0):
    image=Image.new('RGB',(160,120),'white');draw=ImageDraw.Draw(image)
    draw.rectangle((10+index,20,40+index,50),fill='black')
    draw.rectangle((85,65,120,95),outline='black',width=3)
    path=Path(root)/f'view{index}.png';image.save(path);return path


def stage151():
    from seye.image.ingestion import load_image
    cases=[]
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        for mode,orientation in [('RGB',1),('L',1),('P',1),('RGB',6)]:
            image=Image.new('RGB',(480,320),'white');ImageDraw.Draw(image).rectangle((20,10,100,90),fill='black')
            if mode!='RGB':image=image.convert(mode)
            path=root/f'{mode}-{orientation}.png';exif=Image.Exif();exif[274]=orientation;image.save(path,exif=exif)
            raw=path.read_bytes();before=time.perf_counter()
            for _ in range(3):
                raw=path.read_bytes()
                with Image.open(io.BytesIO(raw)) as old:baseline=ImageOps.exif_transpose(old).convert('RGB')
                baseline_digest=hashlib.sha256(raw).hexdigest()
            old_seconds=time.perf_counter()-before;before=time.perf_counter()
            for _ in range(3):actual,source=load_image(path)
            new_seconds=time.perf_counter()-before
            cases.append({'mode':mode,'orientation':orientation,'pixel_equal':baseline.size==actual.size and baseline.tobytes()==actual.tobytes() and baseline_digest==source['sha256'],
                          'size':list(actual.size),'reference_read_decode_hash_seconds':old_seconds,'bounded_read_decode_hash_seconds':new_seconds})
    return {'cases':cases,'measurement_scope':'Both paths read, decode, convert and hash; generated host measurement, no portable speed guarantee',
            'passed':all(c['pixel_equal'] for c in cases)}


def stage152():
    from seye.interface.observer import observe,observe_profiled
    cases=[]
    with tempfile.TemporaryDirectory() as directory:
        a=fixture(directory,0);b=fixture(directory,4)
        for region in (False,True):
            r=observe_profiled(b,previous=a,region_proposals=region,region_mode='refined' if region else 'baseline')
            cases.append({'region_proposals':region,'evidence_equal':r['observation']==observe(b,previous=a,region_proposals=region,region_mode='refined' if region else 'baseline'), 'performance':r['performance']})
    return {'cases':cases,'passed':all(c['evidence_equal'] for c in cases)}


def stage153():
    from seye.recognition.pipeline import FeaturePipeline
    from seye.image.ingestion import load_image
    with tempfile.TemporaryDirectory() as directory:
        image,_=load_image(fixture(directory));p=FeaturePipeline();selections=[['shape'],['appearance','shape'],['interface','shape'],['shape']]
        before=time.perf_counter();old=[p.extract(image,s) for s in selections];separate=time.perf_counter()-before
        before=time.perf_counter();new=p.extract_many(image,selections);shared=time.perf_counter()-before
    return {'packets':len(old),'identical':old==new['packets'],'component_extractions':new['component_extractions'],
            'reused_component_requests':new['reused_component_requests'],'separate_seconds':separate,'shared_seconds':shared,
            'scope':'generated image; feature extraction only; no decode or portable acceleration claim','passed':old==new['packets'] and new['component_extractions']==3}


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True,type=int,choices=range(151,161));p.add_argument('--output',required=True)
    a=p.parse_args();r=globals()[f'stage{a.stage}']();atomic_json(a.output,r,overwrite=True);print(json.dumps(r,sort_keys=True))
    if not r['passed']:raise SystemExit(1)

if __name__=='__main__':main()
