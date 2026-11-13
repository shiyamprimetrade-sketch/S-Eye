"""Stage 88 physical-capture evidence gate, separate from execution success."""


def assess(rows, *, require_reviewed_labels=True):
    if type(require_reviewed_labels) is not bool:
        raise ValueError('require_reviewed_labels must be boolean')
    issues=[]; groups={}
    if not isinstance(rows,list) or not rows:
        return {'schema_version':1,'stage':88,'ready':False,'issues':['No capture evidence'],'groups':[]}
    hashes=set()
    for row in rows:
        if not isinstance(row,dict):
            issues.append('Capture entry must be an object');continue
        identifier=row.get('id','unnamed')
        digest=row.get('sha256')
        valid_hash=isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest)
        if not valid_hash:issues.append(f'{identifier}: valid source hash required')
        elif digest in hashes:issues.append(f'{identifier}: duplicate capture bytes')
        else:hashes.add(digest)
        if row.get('source_kind')!='photograph':issues.append(f'{identifier}: physical photograph required')
        if require_reviewed_labels and row.get('human_confirmed') is not True:issues.append(f'{identifier}: reviewed labels required')
        labels=row.get('expected_classes')
        if require_reviewed_labels and (not isinstance(labels,list) or not labels or any(x not in ('circle','quadrilateral','triangle') for x in labels)):
            issues.append(f'{identifier}: supported reviewed shape labels required')
        target=row.get('target_group')
        if not isinstance(target,str) or not target.strip():issues.append(f'{identifier}: same-target group required');continue
        groups.setdefault(target,[]).append(row)
    summaries=[]
    for target,captures in sorted(groups.items()):
        lights={r.get('lighting') for r in captures if isinstance(r.get('lighting'),str) and r['lighting'] not in ('','unknown','unmeasured')}
        angles={r.get('camera_angle') for r in captures if isinstance(r.get('camera_angle'),str) and r['camera_angle'] not in ('','unknown','unmeasured')}
        if len(captures)<3:issues.append(f'{target}: at least three same-target captures required')
        if len(lights)<2:issues.append(f'{target}: at least two documented physical lighting conditions required')
        if len(angles)<2:issues.append(f'{target}: at least two documented physical camera angles required')
        inventories={tuple(sorted(set(r.get('expected_classes',[])))) for r in captures if isinstance(r.get('expected_classes'),list) and all(isinstance(x,str) for x in r['expected_classes'])}
        if require_reviewed_labels and len(inventories)>1:issues.append(f'{target}: reviewed target inventories differ; review visibility/occlusion')
        summaries.append({'target_group':target,'captures':len(captures),'lighting_conditions':sorted(lights),'camera_angles':sorted(angles)})
    if not groups:issues.append('No documented same-target capture group')
    return {'schema_version':1,'stage':88,'ready':not issues,'issues':issues,'groups':summaries,
            'scope':'declared physical-capture protocol coverage; source bytes and annotation authenticity require independent verification',
            'reviewed_labels_required':require_reviewed_labels,
            'recognition_accuracy':None,
            'recognition_accuracy_validated':False}
