"""One-to-one localization, identity-switch and fragmentation evidence.

Ground-truth identities are supplied independently of tracker outputs. Metrics do
not certify semantic identities, and abstentions count as missing predictions.
"""
from seye.detection.metrics import detection_metrics
from seye.video.temporal import frame_contract


def evaluate(truth_frames, predicted_frames, iou_threshold=.5):
    if not isinstance(truth_frames,list) or not isinstance(predicted_frames,list) or not 1<=len(truth_frames)<=300 or len(truth_frames)!=len(predicted_frames):
        raise ValueError('Equal bounded nonempty frame sequences required')
    totals={'tp':0,'fp':0,'fn':0,'identity_switches':0,'fragmentations':0,'truth_observations':0}
    identities={};last_matched={};segment_matched={};gap={};previous=None;per_frame=[]
    for index,(truth,prediction) in enumerate(zip(truth_frames,predicted_frames)):
        rows=truth.get('objects');size=truth.get('source_size');timestamp=truth.get('timestamp')
        frame_contract(rows,timestamp,size,previous)
        frame_contract(prediction.get('visible'),prediction.get('timestamp'),prediction.get('source_size'),previous)
        if prediction['timestamp']!=timestamp or list(prediction['source_size'])!=list(size):raise ValueError('Predictions and truth must share exact time/grid')
        previous=timestamp;gt_ids=set();pred_ids=set()
        for row in rows:
            identity=row.get('gt_id')
            if not isinstance(identity,str) or not 1<=len(identity)<=128 or identity in gt_ids:raise ValueError('Distinct bounded ground-truth ids required')
            gt_ids.add(identity)
        for row in prediction['visible']:
            identity=row.get('track_uid')
            if not isinstance(identity,str) or not 1<=len(identity)<=128 or identity in pred_ids:raise ValueError('Distinct bounded predicted track ids required')
            pred_ids.add(identity)
        metrics=detection_metrics(rows,prediction['visible'],iou_threshold)
        for gt in set(segment_matched)-gt_ids:
            segment_matched[gt]=False;gap[gt]=False
        matched=set();switches=fragments=0
        for pair in metrics['matches']:
            gt=rows[pair['expected']]['gt_id'];uid=prediction['visible'][pair['predicted']]['track_uid']
            if gt in identities and identities[gt]!=uid:switches+=1
            # Fragmentation counts a visible ground-truth detection that was
            # missed and later matched again; true out-of-view intervals do not.
            if segment_matched.get(gt,False) and gap.get(gt,False):fragments+=1
            identities[gt]=uid;last_matched[gt]=index;matched.add(gt)
            segment_matched[gt]=True;gap[gt]=False
        for gt in gt_ids-matched:
            if segment_matched.get(gt,False):gap[gt]=True
        for key in ('tp','fp','fn'):totals[key]+=metrics[key]
        totals['identity_switches']+=switches;totals['fragmentations']+=fragments;totals['truth_observations']+=len(rows)
        per_frame.append({'frame_index':index,'tp':metrics['tp'],'fp':metrics['fp'],'fn':metrics['fn'],
                          'identity_switches':switches,'fragmentations':fragments})
    denominator=totals['truth_observations']
    return dict(totals,frames=len(truth_frames),iou_threshold=iou_threshold,
                mota=1-(totals['fn']+totals['fp']+totals['identity_switches'])/denominator if denominator else None,
                per_frame=per_frame,representative_validation=False,
                metric_scope='caller-labeled frame boxes and ids; abstentions count as FN; identity mapping retained across gaps')
