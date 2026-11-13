"""Matched-capture known/unknown regression gates; no aggregate tradeoff masking."""
from seye.learning.packet_prototypes import UNKNOWN


def _counts(report):
    if not isinstance(report,dict) or not isinstance(report.get('results'),list) or not report['results']:raise ValueError('Complete evaluation results required')
    known=unknown=correct=rejected=0;ids=set()
    for row in report['results']:
        if row['id'] in ids:raise ValueError('Duplicate evaluation identity')
        ids.add(row['id']);prediction=row['prediction']
        if type(prediction.get('accepted')) is not bool or (prediction['label']==UNKNOWN)==prediction['accepted']:raise ValueError('Inconsistent decision')
        if row['expected']==UNKNOWN:unknown+=1;rejected+=not prediction['accepted']
        else:known+=1;correct+=row['expected']==prediction['label']
    actual={'samples':len(ids),'known_samples':known,'known_correct':correct,'unknown_samples':unknown,'unknown_rejected':rejected}
    if any(type(report.get(k)) is not int or report[k]!=v for k,v in actual.items()):raise ValueError('Evaluation summary/result mismatch')
    digest=report.get('test_capture_sha256')
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('Pinned test capture identity required')
    return actual


def guard(reference,candidate):
    a=_counts(reference);b=_counts(candidate)
    if reference['test_capture_sha256']!=candidate['test_capture_sha256'] or [(r['id'],r['expected']) for r in reference['results']]!=[(r['id'],r['expected']) for r in candidate['results']]:raise ValueError('Comparison requires identical ordered test captures')
    reasons=[]
    if b['known_correct']<a['known_correct']:reasons.append('known_category_regression')
    if b['unknown_rejected']<a['unknown_rejected']:reasons.append('unknown_rejection_regression')
    return {'passed':not reasons,'reasons':reasons,'reference':a,'candidate':b,
            'scope':'fixed generated capture regression only; not real-application release readiness'}
