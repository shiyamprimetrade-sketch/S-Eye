"""Frozen-layout, centered-prototype and learned comparison on the new protocol."""
from learning_batch_data import dataset,protocol
from seye.learning.partitions import validate_partitions
from seye.learning.packet_prototypes import fit as fit_proto,UNKNOWN
from seye.learning.packet_linear import fit as fit_linear
from seye.recognition.packet_decision import decide
from seye.recognition.trained import predict
from seye.core.storage import checksum


def evaluate(testing,function):
    results=[];known=correct=unknown=rejected=0;confusion={}
    for row in testing:
        output=function(row['packet']);expected=row['label'];label=output['label']
        if expected==UNKNOWN:unknown+=1;rejected+=not output['accepted']
        else:known+=1;correct+=expected==label
        confusion.setdefault(expected,{})[label]=confusion.setdefault(expected,{}).get(label,0)+1
        results.append({'id':row['id'],'expected':expected,'prediction':output})
    return {'test_capture_sha256':checksum([{k:r[k] for k in ('id','label','content_sha256')} for r in testing]),'samples':len(testing),'known_samples':known,'known_correct':correct,'unknown_samples':unknown,'unknown_rejected':rejected,
            'confusion':confusion,'results':results,'representative_application_accuracy':None}


def run():
    old=dataset(('geometry','appearance'));new=dataset(('shape',));audit_old=validate_partitions(old);audit_new=validate_partitions(new)
    baseline=fit_proto(old['train'],old['validation']);centered=fit_proto(new['train'],new['validation'])
    linear=fit_linear(new['train'],new['validation'],**protocol()['sgd'])
    outputs={'layout_prototype':evaluate(old['test'],lambda packet:decide(baseline,packet)),
             'centered_prototype':evaluate(new['test'],lambda packet:decide(centered,packet)),
             'centered_sgd':evaluate(new['test'],lambda packet:predict(linear,packet))}
    return {'protocol':protocol(),'protocol_sha256':checksum(protocol()),'partition_audits':{'layout':audit_old,'centered':audit_new},
            'methods':outputs,'attribution':'Centered prototype ablation separates preprocessing gains from SGD; no test selection.',
            'limitations':['Shared generated glyph renderer; no independent application validation.','Only translation/shade variations and two generated unknown designs.','Earlier inspected Stage 109 remains a separate retired comparison.']}
