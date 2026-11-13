"""Explicit preview/apply retention with pinned observations and dependent-link cleanup."""
from seye.core.storage import checksum
from seye.memory.transfer import history_events


def plan(memory,maximum,protected=()):
    memory.verify()
    if type(maximum) is not int or not 0<=maximum<=10000 or not isinstance(protected,(list,tuple)) or any(not isinstance(i,str) for i in protected):raise ValueError('Bounded retention policy required')
    rows=list(memory.db.execute('SELECT sequence,id FROM observations ORDER BY sequence'))
    if len(rows)>10000:raise ValueError('Retention inventory budget exceeded')
    ids={i for s,i in rows};pins=set(protected)
    if not pins<=ids or len(pins)>maximum:raise ValueError('Pinned observations missing or exceed budget')
    keep=set(pins)
    for sequence,identifier in reversed(rows):
        if len(keep)>=maximum:break
        keep.add(identifier)
    result={'format':'seye-retention-plan-v1','maximum':maximum,'protected':sorted(pins),'source_snapshot':checksum(rows),
            'delete':[i for sequence,i in rows if i not in keep]}
    result['plan_sha256']=checksum(result)
    return result


def apply(memory,requested):
    if memory.read_only:raise PermissionError('Retention requires write permission')
    if not isinstance(requested,dict) or requested.get('plan_sha256')!=checksum({k:v for k,v in requested.items() if k!='plan_sha256'}):raise ValueError('Retention plan integrity mismatch')
    if memory.db.in_transaction:raise ValueError('Retention requires an idle connection')
    with memory.db:
        memory.db.execute('BEGIN IMMEDIATE')
        current=plan(memory,requested['maximum'],requested['protected'])
        if current!=requested:raise ValueError('Retention plan stale or changed')
        ids={r[0] for r in memory.db.execute('SELECT id FROM observations')};events=history_events(memory,ids);deleted=set(requested['delete'])
        memory.db.executemany('DELETE FROM observations WHERE id=?',[(i,) for i in deleted])
        removed_events=[checksum(e) for e in events if e['observation_id'] in deleted]
        if removed_events:memory.db.executemany('DELETE FROM seye_history WHERE id=?',[(i,) for i in removed_events])
        for table in ('seye_packet_trees','seye_packet_index_state'):
            if memory.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():memory.db.execute('DELETE FROM '+table)
        memory.verify()
    return {'deleted_observations':len(deleted),'deleted_history_events':len(removed_events),'index_rebuild_required':True}
