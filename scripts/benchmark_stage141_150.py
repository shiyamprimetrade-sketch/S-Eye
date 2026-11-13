#!/usr/bin/env python3
"""Temporal engineering experiments; generated data is explicitly identified."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from seye.core.storage import atomic_json


def stage141():
    from seye.video.temporal import sampling_plan, frame_contract
    p=sampling_plan(3,2)
    frames=[frame_contract([],t,[100,80],p['timestamps'][i-1] if i else None) for i,t in enumerate(p['timestamps'])]
    return {'frames':len(frames),'timestamps':p['timestamps'],'timestamp_scope':p['timestamp_scope'], 'passed':len(frames)==6}


def stage142():
    from seye.video.motion import motion, common_translation
    rows=[motion([10,10,30,30],[10+4*dt,10+2*dt,30+4*dt,30+2*dt],dt) for dt in (.25,1,2)]
    return {'elapsed':[.25,1,2],'velocities':[r['velocity'] for r in rows], 'passed':all(r['velocity']==[4,2] for r in rows)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',type=int,required=True,choices=range(141,151))
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    report=globals()[f'stage{args.stage}']()
    atomic_json(args.output,report,overwrite=True)
    print(json.dumps(report,sort_keys=True))
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
