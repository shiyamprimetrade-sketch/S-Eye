"""Interface experiment accounting. Generated oracles are not application validation."""
from collections import Counter
import math
from seye.detection.metrics import box_iou, valid_box

STATUSES = ('visual_candidate', 'not_found', 'ambiguous', 'execution_error')


def summarize(cases, iou_threshold=.5):
    if not isinstance(cases,list) or not 1 <= len(cases) <= 10000:
        raise ValueError('Nonempty case list required')
    if type(iou_threshold) not in (int,float) or not math.isfinite(iou_threshold) or not 0 < iou_threshold <= 1:
        raise ValueError('IoU threshold must be in (0,1]')
    ids=set(); matrix={expected:{actual:0 for actual in STATUSES} for expected in STATUSES[:-1]}
    dimensions={key:{} for key in ('theme','scale','state','family')}
    errors=[]; correct=completed=tp=fp=fn=change_matches=change_eligible=0
    negative_cases=false_accepts=ambiguous_cases=unsafe_choices=0
    for case in cases:
        if not isinstance(case,dict):raise ValueError('Case must be an object')
        identifier=case.get('id')
        if not isinstance(identifier,str) or not identifier or identifier in ids:
            raise ValueError('Unique nonempty case IDs required')
        ids.add(identifier)
        expected=case.get('expected_status');actual=case.get('observed_status')
        if expected not in STATUSES[:-1] or actual not in STATUSES:
            raise ValueError('Unsupported expected/observed status')
        boxes=case.get('expected_boxes')
        if not isinstance(boxes,list):raise ValueError('Expected boxes required')
        for box in boxes:valid_box(box)
        if expected=='visual_candidate' and len(boxes)!=1:raise ValueError('Unique target needs one box')
        if expected=='ambiguous' and len(boxes)<2:raise ValueError('Ambiguity needs repeated targets')
        if expected=='not_found' and boxes:raise ValueError('Rejected-target case cannot assert supported boxes')
        candidate=case.get('candidate')
        if actual=='visual_candidate':
            if not isinstance(candidate,dict):raise ValueError('Candidate evidence required')
            valid_box(candidate['box'])
        elif candidate is not None:raise ValueError('Abstention/error must not contain an actionable candidate')
        matrix[expected][actual]+=1
        completed+=actual!='execution_error'
        status_ok=expected==actual;correct+=status_ok
        localization_ok=False
        overlap=None
        if expected=='visual_candidate':
            if actual=='visual_candidate':
                overlap=box_iou(boxes[0],candidate['box'])
                localization_ok=overlap>=iou_threshold
            tp+=localization_ok;fn+=not localization_ok
            fp+=actual=='visual_candidate' and not localization_ok
        elif actual=='visual_candidate':fp+=1
        if expected=='not_found':
            negative_cases+=1;false_accepts+=actual=='visual_candidate'
        if expected=='ambiguous':
            ambiguous_cases+=1;unsafe_choices+=actual=='visual_candidate'
        change=case.get('change',{})
        oracle=case.get('expected_change')
        def valid_change(value):
            if not isinstance(value,dict) or 'changed_pixels' not in value or value.get('signal') not in ('pixels_changed','pixels_unchanged','viewport_changed'):
                return False
            count=value.get('changed_pixels')
            if value['signal']=='viewport_changed':return count is None
            return type(count) is int and count >= 0 and ((count==0)==(value['signal']=='pixels_unchanged'))
        if not valid_change(oracle):raise ValueError('Explicit valid change oracle required')
        if actual!='execution_error' and not valid_change(change):raise ValueError('Valid change evidence required')
        change_ok=False
        if actual!='execution_error':
            change_eligible+=1
            change_ok=(change.get('signal')==oracle.get('signal') and
                       change.get('changed_pixels')==oracle.get('changed_pixels'))
            change_matches+=change_ok
        for key,groups in dimensions.items():
            group=str(case.get(key,'unspecified'))
            row=groups.setdefault(group,{'cases':0,'completed':0,'status_matches':0,'localized_unique_targets':0,'unique_targets':0,'false_positives':0,'false_negatives':0,'change_matches':0,'change_eligible':0})
            row['cases']+=1;row['completed']+=actual!='execution_error';row['status_matches']+=status_ok
            row['unique_targets']+=expected=='visual_candidate';row['localized_unique_targets']+=localization_ok
            row['false_positives']+=actual=='visual_candidate' and not localization_ok
            row['false_negatives']+=expected=='visual_candidate' and not localization_ok
            row['change_matches']+=change_ok;row['change_eligible']+=actual!='execution_error'
        if not status_ok or (expected=='visual_candidate' and not localization_ok) or not change_ok:
            errors.append({'id':identifier,'expected_status':expected,'observed_status':actual,
                           'localization_iou':overlap,'change_matches':change_ok,
                           'execution_error':case.get('error')})
    return {'requested_cases':len(cases),'completed_cases':completed,'execution_errors':len(cases)-completed,
            'status_matches':correct,'status_confusion_matrix':matrix,
            'localization':{'iou_threshold':iou_threshold,'true_positives':tp,'false_positives':fp,'false_negatives':fn,
                            'unique_target_cases':tp+fn,'scope':'one candidate per named template; ambiguous inputs require abstention; execution errors count as missed unique targets'},
            'negative_rejection':{'cases':negative_cases,'false_accepts':false_accepts},
            'ambiguity_safety':{'cases':ambiguous_cases,'unsafe_single_choices':unsafe_choices},
            'change_oracle':{'eligible_completed_cases':change_eligible,'exact_matches':change_matches},
            'by_condition':dimensions,'error_examples':errors,
            'representative_application_accuracy':None,'human_expert_equivalence_validated':False}
