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
