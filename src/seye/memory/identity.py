"""Separate source-file, decoded-pixel, feature and observation identities."""
import hashlib
from seye.core.storage import checksum
from seye.memory.store import validate_record


def pixel_identity(image):
    rgb=image.convert('RGB')
    return hashlib.sha256(f'RGB:{rgb.width}:{rgb.height}:'.encode()+rgb.tobytes()).hexdigest()


def identify(record):
    validate_record(record);provenance=record['provenance'];analysis=record.get('analysis')
    source=analysis.get('source') if isinstance(analysis,dict) else None
    if not isinstance(source,dict):source={}
    packet=record.get('packet')
    if packet is not None:
        from seye.recognition.similarity import validate_packet
        validate_packet(packet)
    warnings=[]
    def digest(value,name):
        if value is None:return None
        if isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value):return value
        warnings.append(name+': declaration is not a verified SHA-256 identity')
        return None
    return {'observation_sha256':checksum(record),'source_sha256':digest(provenance.get('source_sha256'),'source'),
            'decoded_pixel_sha256':digest(source.get('pixel_sha256',provenance.get('pixel_sha256')),'pixels'),
            'packet_sha256':checksum(record['packet']) if record.get('packet') is not None else None,
            'feature_schema_sha256':packet['schema_sha256'] if packet is not None else None,
            'model_sha256':digest(provenance.get('model_sha256'),'model'),'identity_warnings':warnings,
            'scope':'Missing historical identities stay null; content hashes are not real-object identity.'}


def occurrence(observation_id,session,event_index):
    if not isinstance(observation_id,str) or len(observation_id)!=64 or any(c not in '0123456789abcdef' for c in observation_id):raise ValueError('Observation digest required')
    if not isinstance(session,str) or not 1<=len(session)<=128 or type(event_index) is not int or not 0<=event_index<=1_000_000_000:raise ValueError('Explicit bounded session/event identity required')
    return checksum({'observation':observation_id,'session':session,'event_index':event_index})
