"""Source-cohort-aware report changes; without labels, changes are not accuracy gains."""
import html,json
from seye.core.storage import read_json,canonical,checksum,atomic_json
from seye.detection.metrics import valid_box
from seye.local.workspace import inside,publish
from seye.local.reports import document


def digest(value):return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def validate(report):
    if not isinstance(report,dict) or report.get('format')!='seye-local-analysis-v1' or type(report.get('schema_version')) is not int or report['schema_version']!=1 or not digest(report.get('workspace_sha256')):raise ValueError('Source-bound local analysis report required')
    if report.get('model_sha256') is not None and not digest(report['model_sha256']):raise ValueError('Invalid declared model digest')
    rows=report.get('items');seen=set()
    if not isinstance(rows,list) or not 1<=len(rows)<=32:raise ValueError('1..32 report rows required')
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not 1<=len(row['id'])<=64 or row['id'] in seen or not digest(row.get('source_sha256')):raise ValueError('Distinct source-bound report IDs required')
        seen.add(row['id']);size=row.get('source_size');boxes=row.get('boxes')
        if not isinstance(size,list) or len(size)!=2 or any(type(v) is not int or v<=0 for v in size) or size[0]*size[1]>4_000_000:raise ValueError('Invalid source grid')
        if not isinstance(boxes,list) or len(boxes)>128 or type(row.get('region_count')) is not int or row['region_count']!=len(boxes):raise ValueError('Region inventory mismatch')
        for box in boxes:
            valid_box(box)
            if not 0<=box[0]<box[2]<=size[0] or not 0<=box[1]<box[3]<=size[1]:raise ValueError('Reported box outside source grid')
        decision=row.get('decision')
        if not isinstance(decision,dict) or decision.get('status') not in ('not_requested','model_label','rejected_or_ambiguous','failed') or decision.get('confidence_probability') is not None:raise ValueError('Explicit uncalibrated decision status required')
        label=decision.get('label')
        if label is not None and (not isinstance(label,str) or len(label)>128):raise ValueError('Bounded training label required')
    if len(canonical(report))>8*1024*1024:raise ValueError('Analysis report exceeds 8 MiB')
    return report


def load_report(path,allowed_root):
    path=inside(path,allowed_root);report=validate(read_json(path,max_bytes=8*1024*1024))
    envelope=read_json(path.parent/'manifest.json',max_bytes=256*1024);payload=envelope.get('payload')
    if not isinstance(payload,dict) or checksum(payload)!=envelope.get('sha256') or payload.get('format')!='seye-local-report-bundle-v1' or payload.get('report_sha256')!=checksum(report) or payload.get('workspace_sha256')!=report['workspace_sha256']:raise ValueError('Report completion manifest mismatch')
    return report


def compare(left,right,allow_partial=False):
    validate(left);validate(right)
    if type(allow_partial) is not bool:raise ValueError('Explicit boolean partial-cohort policy required')
    a={r['id']:r for r in left['items']};b={r['id']:r for r in right['items']};ids=sorted(set(a)|set(b))
    same=left['workspace_sha256']==right['workspace_sha256'] and set(a)==set(b) and all(a[i]['source_sha256']==b[i]['source_sha256'] and a[i]['source_size']==b[i]['source_size'] for i in a if i in b)
    if not same and not allow_partial:raise ValueError('Reports do not share the same complete source cohort')
    rows=[]
    for identifier in ids:
        if identifier not in a:rows.append({'id':identifier,'status':'missing_left'});continue
        if identifier not in b:rows.append({'id':identifier,'status':'missing_right'});continue
        x,y=a[identifier],b[identifier]
        if x['source_sha256']!=y['source_sha256'] or x['source_size']!=y['source_size']:rows.append({'id':identifier,'status':'incomparable_source'});continue
        changed=(x['decision']['status'],x['decision'].get('label'))!=(y['decision']['status'],y['decision'].get('label'))
        rows.append({'id':identifier,'status':'comparable','region_count_delta':y['region_count']-x['region_count'],'decision_changed':changed})
    return {'format':'seye-local-comparison-v1','schema_version':1,'total_source_slots':len(ids),
            'comparable_slots':sum(r['status']=='comparable' for r in rows),'incomparable_or_missing_slots':sum(r['status']!='comparable' for r in rows),
            'changed_decisions':sum(r.get('decision_changed',False) for r in rows),'items':rows,
            'left_report_sha256':checksum(left),'right_report_sha256':checksum(right),'accuracy_change':None,
            'scope':'source-matched proposal/decision changes; unlabelled inputs cannot establish accuracy improvement'}


def export_comparison(left,right,destination,allowed_root,allow_partial=False):
    report=compare(load_report(left,allowed_root),load_report(right,allowed_root),allow_partial)
    def build(stage):
        atomic_json(stage/'comparison.json',report)
        body='<p class="badge">Changes, not accuracy gains</p><pre>'+html.escape(json.dumps(report,indent=2))+'</pre>'
        (stage/'compare.html').write_text(document('S-Eye · experiment comparison',body),encoding='utf-8')
        return {'format':'seye-comparison-bundle-v1','schema_version':1,'comparison_sha256':checksum(report),'files':['comparison.json','compare.html']}
    return publish(destination,allowed_root,build)
