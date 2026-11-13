"""Verified portable observation/history bundles and new-destination atomic recovery."""
import json,os,tempfile
from pathlib import Path
from seye.core.storage import read_json,atomic_json,canonical,checksum
from seye.memory.store import Memory,validate_record
from seye.memory.identity import occurrence


def history_events(memory,ids):
    if not memory.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='seye_history'").fetchone():return []
    rows=list(memory.db.execute('SELECT id,payload,sha256 FROM seye_history ORDER BY id'))
    if len(rows)>10000:raise ValueError('Bundle history budget exceeded')
    events=[]
    for identifier,payload,digest in rows:
        event=json.loads(payload)
        if checksum(event)!=identifier or digest!=identifier:raise ValueError('History checksum mismatch')
        _validate_event(event,ids);events.append(event)
    return events


def _validate_event(event,ids):
    if not isinstance(event,dict) or event.get('observation_id') not in ids or event.get('identity_origin')!='caller_asserted':raise ValueError('Missing history source or unsupported identity claim')
    for key,maximum in (('entity',128),('link_basis',256)):
        if not isinstance(event.get(key),str) or not 1<=len(event[key])<=maximum:raise ValueError('Invalid history metadata')
    if occurrence(event['observation_id'],event['session'],event['event_index'])!=event.get('occurrence_sha256'):raise ValueError('History occurrence identity mismatch')


def export_bundle(memory,path):
    memory.verify();rows=list(memory.db.execute('SELECT id,payload FROM observations ORDER BY sequence'))
    if len(rows)>10000:raise ValueError('Bundle observation budget exceeded')
    observations=[json.loads(p) for i,p in rows];ids={i for i,p in rows}
    payload={'format':'seye-memory-bundle-v1','observations':observations,'history':history_events(memory,ids),
             'observation_order_sha256':checksum([i for i,p in rows]),'derived_indexes_included':False}
    envelope={'payload':payload,'sha256':checksum(payload)}
    if len(canonical(envelope))>16*1024*1024:raise ValueError('Bundle byte budget exceeded')
    atomic_json(path,envelope)
    return {'observations':len(observations),'history_events':len(payload['history']),'bundle_sha256':envelope['sha256']}


def restore_bundle(bundle,destination):
    envelope=read_json(bundle);payload=envelope.get('payload')
    if not isinstance(payload,dict) or envelope.get('sha256')!=checksum(payload) or payload.get('format')!='seye-memory-bundle-v1':raise ValueError('Bundle integrity/format mismatch')
    observations=payload.get('observations');events=payload.get('history')
    if not isinstance(observations,list) or len(observations)>10000 or not isinstance(events,list) or len(events)>10000:raise ValueError('Invalid bundle inventory')
    ids=[]
    for record in observations:validate_record(record);ids.append(checksum(record))
    if len(set(ids))!=len(ids) or checksum(ids)!=payload.get('observation_order_sha256'):raise ValueError('Bundle observation identity/order mismatch')
    identity_set=set(ids)
    for event in events:_validate_event(event,identity_set)
    if len({checksum(e) for e in events})!=len(events):raise ValueError('Duplicate bundle history events')
    destination=Path(destination)
    if destination.exists() or destination.is_symlink():raise FileExistsError('Recovery never overwrites an existing destination')
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.seye-restore-',suffix='.sqlite3',dir=destination.parent);os.close(fd);temporary=Path(name);memory=None
    try:
        memory=Memory(temporary)
        with memory.db:
            memory.db.executemany('INSERT INTO observations(id,payload,sha256) VALUES (?,?,?)',[(identifier,canonical(record).decode(),identifier) for identifier,record in zip(ids,observations)])
            memory.db.execute('CREATE TABLE seye_history(id TEXT PRIMARY KEY,entity TEXT NOT NULL,payload TEXT NOT NULL,sha256 TEXT NOT NULL)')
            memory.db.execute('CREATE INDEX seye_history_entity ON seye_history(entity)')
            memory.db.executemany('INSERT INTO seye_history VALUES (?,?,?,?)',[(checksum(e),e['entity'],canonical(e).decode(),checksum(e)) for e in events])
        result=memory.verify();history_events(memory,set(ids));memory.close();memory=None
        os.link(temporary,destination) # Exclusive publication; concurrent destinations cannot be replaced.
        return dict(result,history_events=len(events),bundle_sha256=envelope['sha256'],index_rebuild_required=True)
    finally:
        if memory is not None:memory.close()
        temporary.unlink(missing_ok=True)
