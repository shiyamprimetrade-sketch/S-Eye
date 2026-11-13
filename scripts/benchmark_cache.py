#!/usr/bin/env python3
"""Measure repeated-input descriptor caching, not general image-analysis acceleration."""
import argparse
import hashlib
from pathlib import Path
import platform
import sys
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from PIL import Image, ImageDraw
from seye.core.storage import atomic_json
from seye.image.ingestion import load_image
from seye.recognition.features import extract, FEATURE_VERSION
from seye.recognition.cache import FeatureCache


def benchmark():
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'generated.png';image=Image.new('RGB',(400,400),'white')
        ImageDraw.Draw(image).ellipse((80,80,320,320),outline='black',width=8);image.save(path)
        count=20; uncached=[]; cpu=time.process_time(); wall=time.perf_counter()
        for _ in range(count):decoded,_=load_image(path);uncached.append(extract(decoded))
        uncached_wall=time.perf_counter()-wall;uncached_cpu=time.process_time()-cpu
        cache=FeatureCache();cached=[];cpu=time.process_time();wall=time.perf_counter()
        for _ in range(count):cached.append(cache.from_file(path)[0])
        cached_wall=time.perf_counter()-wall;cached_cpu=time.process_time()-cpu
        return {'schema_version':1,'source_kind':'synthetic','runtime':{'python':platform.python_version(),'system':platform.system()},
                'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'feature_version':FEATURE_VERSION,
                'code_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src/seye/recognition/cache.py',ROOT/'src/seye/recognition/features.py',Path(__file__).resolve())},
                'repeated_queries':count,'features_identical':cached==uncached,'uncached_wall_seconds':uncached_wall,
                'cached_wall_seconds':cached_wall,'uncached_python_cpu_seconds':uncached_cpu,'cached_python_cpu_seconds':cached_cpu,
                'observed_wall_ratio':uncached_wall/cached_wall,'cache':cache.statistics(),
                'scope':'one repeated generated image, descriptor path only; read/hash/decode retained; one host sample',
                'limitations':['Not a video/detection/unique-image acceleration claim.','Estimated Python cache size is not total/native memory.','No Android/device throughput validation.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=benchmark();atomic_json(args.output,result);print(result)
