"""Schema-checked component-balanced similarity, never a truth probability."""
import math
from seye.core.storage import checksum


def validate_packet(packet):
    if not isinstance(packet,dict):raise ValueError('Feature packet required')
    schema=packet.get('schema');values=packet.get('features')
    if not isinstance(schema,dict) or schema.get('version')!='seye-feature-pipeline-v1' or packet.get('schema_sha256')!=checksum(schema):raise ValueError('Feature schema identity mismatch')
    components=schema.get('components');dimension=schema.get('dimension')
    if type(dimension) is not int or not 1<=dimension<=4096 or not isinstance(components,list) or not 1<=len(components)<=8:raise ValueError('Invalid feature schema')
    names=set();offset=0
    for row in components:
        if not isinstance(row,dict):raise ValueError('Component object required')
        name=row.get('name');version=row.get('version');count=row.get('dimension')
        if not isinstance(name,str) or not name or name in names or not isinstance(version,str) or not version or type(count) is not int or count<=0 or type(row.get('offset')) is not int or row['offset']!=offset:raise ValueError('Invalid component layout')
        names.add(name);offset+=count
    if offset!=dimension or not isinstance(values,list) or len(values)!=dimension or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e6 for v in values):raise ValueError('Invalid feature vector')
    return packet


def compare(first,second,weights=None):
    validate_packet(first);validate_packet(second)
    if first['schema_sha256']!=second['schema_sha256']:raise ValueError('Incompatible feature schemas')
    names={c['name'] for c in first['schema']['components']}
    if weights is None:weights={name:1.0 for name in names}
    if not isinstance(weights,dict) or set(weights)!=names or any(type(w) not in (int,float) or not math.isfinite(w) or not 0<w<=100 for w in weights.values()):raise ValueError('Explicit positive weights for every component required')
    components=[];total=sum(weights.values());squared=0
    for row in first['schema']['components']:
        start=row['offset'];stop=start+row['dimension']
        mse=sum((a-b)**2 for a,b in zip(first['features'][start:stop],second['features'][start:stop]))/row['dimension']
        contribution=mse*weights[row['name']]/total;squared+=contribution
        components.append({'name':row['name'],'rms_distance':math.sqrt(mse),'weighted_squared_contribution':contribution})
    distance=math.sqrt(squared)
    return {'distance':distance,'similarity':1/(1+distance),'components':components,'schema_sha256':first['schema_sha256'],'confidence_probability':None}
