"""Uncalibrated learned scores gated by schema-bound prototype support."""
from seye.learning.packet_linear import scores
from seye.recognition.packet_decision import decide
from seye.learning.packet_prototypes import UNKNOWN
from seye.core.storage import checksum


def predict(model,packet):
    support=decide(model['support_prototypes'],packet);values=scores(model,packet)
    candidates=sorted([{'label':label,'raw_softmax_score':value,'label_origin':'training_records'} for label,value in zip(model['classes'],values)],key=lambda r:(-r['raw_softmax_score'],r['label']))
    first=candidates[0]
    if not support['accepted']:accepted=False;reason='prototype_support_rejected'
    elif first['label']!=support['label']:accepted=False;reason='linear_prototype_disagreement'
    elif first['raw_softmax_score']<.5:accepted=False;reason='insufficient_uncalibrated_linear_score'
    else:accepted=True;reason='linear_and_prototype_agree_within_support'
    return {'label':first['label'] if accepted else UNKNOWN,'accepted':accepted,'reason':reason,
            'candidates':candidates,'prototype_support':support,'confidence_probability':None,
            'model_sha256':checksum(model),'schema_sha256':packet['schema_sha256'],
            'scope':'generated-data learned scores and conservative support; not calibrated truth probabilities'}
