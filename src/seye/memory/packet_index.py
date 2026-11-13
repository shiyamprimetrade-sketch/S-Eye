"""Derived persistent schema-specific exact KD trees; observations remain authoritative.

Distance pruning does not make end-to-end queries sublinear: integrity verification
and snapshot freshness still scan the authoritative observation inventory.
"""
import json,math
from seye.core.storage import checksum,canonical
from seye.recognition.similarity import validate_packet


def project(packet):
    validate_packet(packet);parts=packet['schema']['components'];result=[]
    for part in parts:
        start=part['offset'];stop=start+part['dimension'];scale=math.sqrt(1/(len(parts)*part['dimension']))
        result.extend(v*scale for v in packet['features'][start:stop])
    return result


def _tree(points):
    if not points:return None
    dimension=len(points[0]['vector']);axis=max(range(dimension),key=lambda a:max(p['vector'][a] for p in points)-min(p['vector'][a] for p in points))
    points=sorted(points,key=lambda p:(p['vector'][axis],p['id']));middle=len(points)//2
    return {'point':points[middle],'axis':axis,'left':_tree(points[:middle]),'right':_tree(points[middle+1:])}


def _snapshot(memory):
    memory.verify()
    rows=list(memory.db.execute('SELECT sequence,id FROM observations ORDER BY sequence'))
    if len(rows)>10000:raise ValueError('Index inventory exceeds 10000 observations')
    return checksum(rows)


def rebuild(memory):
    if memory.read_only:raise PermissionError('Index rebuild requires write permission')
    snapshot=_snapshot(memory);groups={};values=0;indexed=0
    for identifier,payload in memory.db.execute('SELECT id,payload FROM observations ORDER BY sequence'):
        record=json.loads(payload);packet=record.get('packet')
        if packet is None:continue
        vector=project(packet);values+=len(vector);indexed+=1
        if values>1_000_000:raise ValueError('Index vector-value budget exceeded')
        point={'id':identifier,'vector':vector,'packet_sha256':checksum(packet),
               'source_sha256':record['provenance'].get('source_sha256'),
               'pixel_sha256':record.get('analysis',{}).get('source',{}).get('pixel_sha256',record['provenance'].get('pixel_sha256'))}
        groups.setdefault(packet['schema_sha256'],[]).append(point)
    trees={schema:{'format':'seye-kd-index-v1','schema_sha256':schema,'snapshot':snapshot,'count':len(points),'tree':_tree(points)} for schema,points in groups.items()}
    if any(len(canonical(value))>32*1024*1024 for value in trees.values()):raise ValueError('Index serialization budget exceeded')
    with memory.db:
        memory.db.execute('CREATE TABLE IF NOT EXISTS seye_packet_trees(schema_sha256 TEXT PRIMARY KEY,payload TEXT NOT NULL,sha256 TEXT NOT NULL)')
        memory.db.execute('DELETE FROM seye_packet_trees')
        for schema,payload in trees.items():memory.db.execute('INSERT INTO seye_packet_trees VALUES (?,?,?)',(schema,canonical(payload).decode(),checksum(payload)))
    return {'indexed_observations':indexed,'schemas':len(trees),'source_snapshot':snapshot,'method':'exact balanced KD trees; derived cache, not authoritative memory'}


def load_tree(memory,schema):
    snapshot=_snapshot(memory)
    exists=memory.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='seye_packet_trees'").fetchone()
    if not exists:raise ValueError('Packet index absent; explicit rebuild required')
    row=memory.db.execute('SELECT payload,sha256 FROM seye_packet_trees WHERE schema_sha256=?',(schema,)).fetchone()
    if row is None:return None
    if len(row[0].encode())>32*1024*1024:raise ValueError('Index serialization budget exceeded')
    payload=json.loads(row[0])
    if checksum(payload)!=row[1] or payload.get('format')!='seye-kd-index-v1' or payload.get('schema_sha256')!=schema:raise ValueError('Packet index integrity mismatch')
    if payload.get('snapshot')!=snapshot:raise ValueError('Packet index stale; explicit rebuild required')
    return payload
