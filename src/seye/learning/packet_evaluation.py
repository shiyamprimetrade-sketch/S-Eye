"""Locked-test accounting for packet models; never fit or select parameters here."""
from seye.learning.packet_prototypes import validate_records,UNKNOWN,nearest
from seye.recognition.packet_decision import decide
from seye.learning.packet_calibration import support


def evaluate(model,testing,calibration=None):
    validate_records(testing)
    fitted=model['training_identities']+model['validation_identities']
    for key in ('id','group','content_sha256'):
        if {r[key] for r in fitted}&{r[key] for r in testing}:raise ValueError('Test leakage: '+key)
    results=[];confusion={};per_class={};known_correct=unknown_rejected=known=unknown=0;raw_loss=calibrated_loss=0
    for row in testing:
        decision=decide(model,row['packet']);expected=row['label'];label=decision['label']
        if expected not in model['classes']+[UNKNOWN]:raise ValueError('Test label outside declared taxonomy')
        confusion.setdefault(expected,{})[label]=confusion.setdefault(expected,{}).get(label,0)+1
        category=per_class.setdefault(expected,{'samples':0,'correct':0});category['samples']+=1;category['correct']+=label==expected
        if expected==UNKNOWN:unknown+=1;unknown_rejected+=not decision['accepted']
        else:known+=1;known_correct+=label==expected
        top=nearest(model,row['packet'])[0];truth=top['label']==expected;raw=1/(1+top['distance']);raw_loss+=(raw-int(truth))**2
        empirical=None
        if calibration is not None:
            empirical=support(model,calibration,row['packet'])['validation_support_estimate'];calibrated_loss+=(empirical-int(truth))**2
        results.append({'id':row['id'],'expected':expected,'decision':decision,'top_known_label':top['label'],'empirical_validation_support':empirical,'source_kind':row.get('source_kind','unspecified')})
    n=len(testing)
    return {'samples':n,'known_samples':known,'known_correct':known_correct,'unknown_samples':unknown,'unknown_rejected':unknown_rejected,
            'confusion':confusion,'per_class':per_class,'results':results,'raw_correctness_proxy_brier':raw_loss/n,
            'empirical_support_brier':calibrated_loss/n if calibration is not None else None,
            'representative_application_accuracy':None,'parameter_selection_on_test':False}
