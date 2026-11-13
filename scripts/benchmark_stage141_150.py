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


def stage143():
    from seye.video.continuity import ContinuityTracker
    t=ContinuityTracker(); frames=[]
    for i in range(8):
        rows=[{'class':'region','box':[10+3*i,10,30+3*i,30]},{'class':'region','box':[90-2*i,45,110-2*i,65]}]
        frames.append(t.update(rows[::-1] if i%2 else rows,i/2,[140,80]))
    return {'frames':8,'track_ids':[[r['track_id'] for r in f['visible']] for f in frames],
            'passed':all([r['track_id'] for r in f['visible']]==[1,2] for f in frames)}


def stage144():
    from seye.video.continuity import ContinuityTracker
    t=ContinuityTracker(session_id='generated-identity',max_gap_seconds=1)
    row={'class':'region','box':[10,10,30,30]}
    frames=[t.update([row],0,[100,80]),t.update([row],2,[100,80]),t.update([row],3,[200,160],discontinuity=True)]
    uids=[f['visible'][0]['track_uid'] for f in frames]
    return {'track_uids':uids,'retirements':[f['retirements'] for f in frames], 'passed':len(set(uids))==3}


def stage145():
    from seye.video.continuity import ContinuityTracker
    t=ContinuityTracker(session_id='gap')
    row=lambda x:{'class':'region','box':[x,10,x+20,30]}
    a=t.update([row(10)],0,[100,80]);b=t.update([row(12)],.5,[100,80])
    missing=t.update([],1,[100,80]);recovered=t.update([row(16)],1.5,[100,80])
    return {'missing':missing['unobserved'],'recovery':recovered['visible'][0]['association'],
            'same_geometric_track':recovered['visible'][0]['track_id']==a['visible'][0]['track_id'],
            'passed':recovered['visible'][0]['association']=='tentative_reacquisition'}


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
