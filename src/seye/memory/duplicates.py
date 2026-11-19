"""Separate exact source, pixel and feature equivalence; never automatically erase history."""
import json
from seye.core.storage import checksum
from seye.memory.identity import identify
from seye.recognition.similarity import validate_packet


def groups(memory):
    memory.verify();inventory=list(memory.db.execute('SELECT id,payload FROM observations ORDER BY sequence'))
    if len(inventory)>10000:raise ValueError('Duplicate inventory budget exceeded')
    buckets={key:{} for key in ('source_content','decoded_pixels','feature_equivalence')}
    for identifier,payload in inventory:
        record=json.loads(payload);identity=identify(record)
        for group,key in (('source_content','source_sha256'),('decoded_pixels','decoded_pixel_sha256')):
            value=identity[key]
            if value is not None:buckets[group].setdefault(value,[]).append(identifier)
        packet=record.get('packet')
        if packet is not None:
            validate_packet(packet);key=checksum({'schema':packet['schema_sha256'],'features':packet['features']})
            buckets['feature_equivalence'].setdefault(key,[]).append(identifier)
    return {'groups':{kind:[{'digest':digest,'observations':ids} for digest,ids in sorted(values.items()) if len(ids)>1] for kind,values in buckets.items()},
            'observations':len(inventory),'automatic_deletion':False,
            'scope':'Exact hashes and descriptor equivalence only; same features do not establish same scene/object.'}
