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
        from seye.memory.identity import identify
        identity=identify(record)
        point={'id':identifier,'vector':vector,'packet_sha256':checksum(packet),
               'source_sha256':identity['source_sha256'],
               'pixel_sha256':identity['decoded_pixel_sha256']}
        groups.setdefault(packet['schema_sha256'],[]).append(point)
    trees={schema:{'format':'seye-kd-index-v1','schema_sha256':schema,'snapshot':snapshot,'count':len(points),'tree':_tree(points)} for schema,points in groups.items()}
    if any(len(canonical(value))>32*1024*1024 for value in trees.values()):raise ValueError('Index serialization budget exceeded')
    with memory.db:
        memory.db.execute('CREATE TABLE IF NOT EXISTS seye_packet_trees(schema_sha256 TEXT PRIMARY KEY,payload TEXT NOT NULL,sha256 TEXT NOT NULL)')
        memory.db.execute('CREATE TABLE IF NOT EXISTS seye_packet_index_state(id INTEGER PRIMARY KEY,snapshot TEXT NOT NULL)')
        memory.db.execute('INSERT OR REPLACE INTO seye_packet_index_state VALUES (1,?)',(snapshot,))
        memory.db.execute('DELETE FROM seye_packet_trees')
        for schema,payload in trees.items():memory.db.execute('INSERT INTO seye_packet_trees VALUES (?,?,?)',(schema,canonical(payload).decode(),checksum(payload)))
    return {'indexed_observations':indexed,'schemas':len(trees),'source_snapshot':snapshot,'method':'exact balanced KD trees; derived cache, not authoritative memory'}


def load_tree(memory,schema):
    snapshot=_snapshot(memory)
    exists=memory.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='seye_packet_trees'").fetchone()
    if not exists:raise ValueError('Packet index absent; explicit rebuild required')
    if not memory.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='seye_packet_index_state'").fetchone():raise ValueError('Packet index format requires explicit rebuild')
    state=memory.db.execute('SELECT snapshot FROM seye_packet_index_state WHERE id=1').fetchone()
    if state is None or state[0]!=snapshot:raise ValueError('Packet index stale; explicit rebuild required')
    row=memory.db.execute('SELECT payload,sha256 FROM seye_packet_trees WHERE schema_sha256=?',(schema,)).fetchone()
    if row is None:return None
    if len(row[0].encode())>32*1024*1024:raise ValueError('Index serialization budget exceeded')
    payload=json.loads(row[0])
    if checksum(payload)!=row[1] or payload.get('format')!='seye-kd-index-v1' or payload.get('schema_sha256')!=schema:raise ValueError('Packet index integrity mismatch')
    if payload.get('snapshot')!=snapshot:raise ValueError('Packet index stale; explicit rebuild required')
    return payload


def query(memory,packet,limit=5,exclude_sources=(),maximum_distance=None):
    validate_packet(packet)
    if type(limit) is not int or not 1<=limit<=100:raise ValueError('Query limit must be 1..100')
    if not isinstance(exclude_sources,(list,tuple)) or len(exclude_sources)>100 or any(not isinstance(v,str) or len(v)!=64 or any(c not in '0123456789abcdef' for c in v) for v in exclude_sources):raise ValueError('Bounded explicit source digests required')
    if maximum_distance is not None and (type(maximum_distance) not in (int,float) or not math.isfinite(maximum_distance) or not 0<=maximum_distance<=1e6):raise ValueError('Finite nonnegative maximum distance required')
    search_limit=max(2,limit);cap=maximum_distance if maximum_distance is not None else math.inf
    payload=load_tree(memory,packet['schema_sha256']);vector=project(packet);best=[];visited=evaluated=0;seen=set()
    def visit(node):
        nonlocal visited,evaluated
        if node is None:return
        visited+=1
        if visited>10000:raise ValueError('Index traversal budget exceeded')
        point=node['point'];axis=node['axis'];identifier=point['id'];values=point['vector']
        if identifier in seen or type(axis) is not int or not 0<=axis<len(vector) or not isinstance(values,list) or len(values)!=len(vector) or any(type(v) not in (int,float) or not math.isfinite(v) for v in values):raise ValueError('Invalid index geometry')
        seen.add(identifier);delta=vector[axis]-values[axis]
        near,far=('left','right') if delta<0 else ('right','left')
        if point.get('source_sha256') not in exclude_sources and point.get('pixel_sha256') not in exclude_sources:
            evaluated+=1;distance=math.sqrt(sum((a-b)**2 for a,b in zip(vector,values)))
            if distance<=cap:best.append({'id':identifier,'distance':distance,'source_sha256':point.get('source_sha256'),'pixel_sha256':point.get('pixel_sha256'),'packet_sha256':point['packet_sha256']})
            best.sort(key=lambda r:(r['distance'],r['id']));del best[search_limit:]
        visit(node.get(near))
        bound=min(cap,best[-1]['distance'] if len(best)>=search_limit else math.inf)
        if delta*delta<=bound**2+1e-15:visit(node.get(far))
    if payload is not None:visit(payload['tree'])
    # Returned candidates must still agree with authoritative packet contents.
    for item in best:
        row=memory.db.execute('SELECT payload FROM observations WHERE id=?',(item['id'],)).fetchone()
        if row is None or checksum(json.loads(row[0]).get('packet'))!=item['packet_sha256']:raise ValueError('Indexed candidate/source mismatch')
    ambiguous=len(best)>1 and abs(best[0]['distance']-best[1]['distance'])<=1e-12
    return {'matches':best[:limit],'ambiguous_top_distance':ambiguous,'visited_nodes':visited,'distance_evaluations':evaluated,
            'indexed_points':payload['count'] if payload else 0,'schema_sha256':packet['schema_sha256'],
            'scope':'exact component-balanced feature distance; same source exclusion is explicit; similarity is not semantic identity',
            'integrity_cost':'authoritative verification and snapshot scan remain linear'}
