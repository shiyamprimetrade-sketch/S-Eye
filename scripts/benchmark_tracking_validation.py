#!/usr/bin/env python3
"""Generated multi-sequence tracking stress test; detection oracles are not real UI vision."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from seye.video.continuity import ContinuityTracker
from seye.video.tracking import Tracker
from seye.video.evaluation import evaluate


def sequence(kind, offset=0):
    truth=[];samples=[]
    for i in range(12):
        stamp=i/2
        if kind=='irregular':stamp=[0,.2,.7,1,1.7,2,2.3,3,3.4,4,4.8,5.5][i]
        a=10+3*i+offset;b=100-2*i+offset;y2=55
        if kind in ('crossing','merged'):a=10+6*i+offset;b=100-6*i+offset;y2=10
        if kind=='acceleration':a=10+i*i+offset
        if kind=='irregular':a=10+4*stamp+offset
        boxes=[[a,10,a+20,30],[b,y2,b+20,y2+20]]
        prefix='after-cut-' if kind=='cut' and i>=6 else ''
        rows=[{'gt_id':prefix+str(k),'class':'region','box':box} for k,box in enumerate(boxes)]
        detections=[{k:v for k,v in row.items() if k!='gt_id'} for row in rows]
        if kind=='short_gap' and i==4:detections=detections[1:]
        if kind=='long_gap' and 3<=i<=7:detections=detections[1:]
        if kind=='merged' and max(a,b)<min(a+20,b+20):
            detections=[{'class':'region','box':[min(a,b),10,max(a,b)+20,30]}]
        if kind=='clutter':detections.append({'class':'region','box':[180,90,195,105]})
        if i%2:detections.reverse()
        truth.append({'timestamp':stamp,'source_size':[220,120],'objects':deepcopy(rows)})
        samples.append({'timestamp':stamp,'source_size':[220,120],'detections':deepcopy(detections),'discontinuity':kind=='cut' and i==6})
    return truth,samples


def run():
    cases=[]
    kinds=('steady','short_gap','long_gap','crossing','merged','clutter','cut','acceleration','irregular')
    for kind in kinds:
        for offset in (0,2,5):
            truth,samples=sequence(kind,offset)
            tracker=ContinuityTracker(session_id=f'{kind}-{offset}');legacy=Tracker();frames=[];baseline=[]
            for sample in samples:
                frames.append(tracker.update(sample['detections'],sample['timestamp'],sample['source_size'],sample['discontinuity']))
                old=legacy.update(sample['detections'],sample['timestamp'])
                old['source_size']=sample['source_size']
                for row in old['visible']:row['track_uid']=f"legacy:{row['track_id']}"
                baseline.append(old)
            cases.append({'scenario':kind,'offset':offset,'conservative':evaluate(truth,frames),'legacy':evaluate(truth,baseline),
                          'unresolved_observations':sum(len(f['unresolved_detection_indices']) for f in frames)})
    totals={}
    for method in ('legacy','conservative'):
        totals[method]={key:sum(c[method][key] for c in cases) for key in ('tp','fp','fn','identity_switches','fragmentations','truth_observations')}
    return {'schema_version':1,'generated_sequences':len(cases),'frames':sum(c['conservative']['frames'] for c in cases),
            'totals':totals,'cases':cases,'representative_validation':False,
            'limitations':['Automatic box/detection oracles isolate association behavior; not segmentation or application validation.',
                           'Translated correlated fixtures are stress cases, not independent natural samples.',
                           'Ambiguity abstention is counted as FN; clutter and merged-region errors stay in all denominators.',
                           'Legacy comparator is unchanged and does not accept caller scene-cut signals.']}
