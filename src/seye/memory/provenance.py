"""Expose stored evidence and uncertainty without upgrading historical claims."""
import json
from seye.memory.identity import identify


def summarize(record):
    identity=identify(record);analysis=record.get('analysis',{})
    if not isinstance(analysis,dict):analysis={}
    selection=analysis.get('selection',analysis)
    if not isinstance(selection,dict):selection={}
    accepted=selection.get('accepted');candidates=analysis.get('candidates')
    if not isinstance(candidates,list):candidates=[]
    return {'identity':identity,'provenance':record['provenance'],
            'stored_label':selection.get('label'),'stored_acceptance':accepted if type(accepted) is bool else None,
            'stored_reason':selection.get('reason'),'confidence_probability':None,
            'raw_candidate_scores':[{k:c[k] for k in ('label','raw_softmax_score') if k in c} for c in candidates if isinstance(c,dict)],
            'uncertainty_scope':'Stored training-label assertions and raw scores are not verified truth; missing historical values stay null.'}


def audit(memory):
    memory.verify();rows=list(memory.db.execute('SELECT id,payload FROM observations ORDER BY sequence'))
    if len(rows)>10000:raise ValueError('Provenance audit inventory exceeded')
    missing_source=missing_pixels=model_bound=0
    for identifier,payload in rows:
        item=summarize(json.loads(payload));identity=item['identity']
        missing_source+=identity['source_sha256'] is None;missing_pixels+=identity['decoded_pixel_sha256'] is None
        model_bound+=identity['model_sha256'] is not None
    return {'observations':len(rows),'missing_source_identity':missing_source,'missing_pixel_identity':missing_pixels,
            'declared_model_identities':model_bound,'label_truth_authenticated':False,'confidence_probabilities_inferred':False}
