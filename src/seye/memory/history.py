"""Caller-asserted target histories, not inferred persistent object identity."""
import json
from seye.core.storage import checksum,canonical
from seye.memory.identity import occurrence


def _entity(value):
    if not isinstance(value,str) or not 1<=len(value)<=128:raise ValueError('Bounded explicit entity key required')


def link(memory,entity,observation_id,session,event_index,reason='caller_asserted_same_target'):
    if memory.read_only:raise PermissionError('History mutation requires write permission')
    _entity(entity)
    if not isinstance(reason,str) or not 1<=len(reason)<=256:raise ValueError('Explicit bounded link reason required')
    if memory.get(observation_id) is None:raise ValueError('History source observation not found')
    event={'entity':entity,'observation_id':observation_id,'session':session,'event_index':event_index,
           'occurrence_sha256':occurrence(observation_id,session,event_index),'link_basis':reason,'identity_origin':'caller_asserted'}
    identifier=checksum(event)
    with memory.db:
        memory.db.execute('CREATE TABLE IF NOT EXISTS seye_history(id TEXT PRIMARY KEY,entity TEXT NOT NULL,payload TEXT NOT NULL,sha256 TEXT NOT NULL)')
        memory.db.execute('CREATE INDEX IF NOT EXISTS seye_history_entity ON seye_history(entity)')
        count=memory.db.execute('SELECT count(*) FROM seye_history').fetchone()[0]
        if count>=10000 and memory.db.execute('SELECT 1 FROM seye_history WHERE id=?',(identifier,)).fetchone() is None:raise ValueError('History event budget exceeded')
        memory.db.execute('INSERT OR IGNORE INTO seye_history VALUES (?,?,?,?)',(identifier,entity,canonical(event).decode(),identifier))
    return {'event_id':identifier,'identity_origin':'caller_asserted'}


def read(memory,entity,limit=50):
    _entity(entity);memory.verify()
    if type(limit) is not int or not 1<=limit<=100:raise ValueError('History limit must be 1..100')
    if not memory.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='seye_history'").fetchone():return {'events':[],'complete':True,'total':0}
    rows=list(memory.db.execute('SELECT id,payload,sha256 FROM seye_history WHERE entity=?',(entity,)))
    if len(rows)>10000:raise ValueError('History read budget exceeded')
    events=[]
    for identifier,payload,digest in rows:
        event=json.loads(payload)
        if checksum(event)!=digest or digest!=identifier or event.get('entity')!=entity:raise ValueError('History integrity mismatch')
        if occurrence(event['observation_id'],event['session'],event['event_index'])!=event.get('occurrence_sha256'):raise ValueError('History occurrence mismatch')
        available=memory.db.execute('SELECT 1 FROM observations WHERE id=?',(event['observation_id'],)).fetchone() is not None
        events.append(dict(event,event_id=identifier,observation_available=available))
    events.sort(key=lambda r:(r['session'],r['event_index'],r['event_id']))
    return {'events':events[-limit:],'total':len(events),'complete':len(events)<=limit,
            'scope':'caller links; event order is session-local, not inferred global time or semantic identity'}
