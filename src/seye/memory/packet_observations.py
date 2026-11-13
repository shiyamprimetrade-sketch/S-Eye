"""Persist structured trained observations without storing source pixels or false certainty."""
from copy import deepcopy
from seye.recognition.similarity import validate_packet
from seye.memory.store import Memory


def remember(path,request_id,packet,result):
    validate_packet(packet)
    record={'schema_version':1,'features':None,'packet':deepcopy(packet),'analysis':deepcopy(result),
            'provenance':{'kind':'trained_visual_observation','request_id':request_id,
                          'source_sha256':result['source']['sha256'],'model_sha256':result['model_sha256']}}
    memory=Memory(path)
    try:return {'observation_id':memory.put(record),'integrity':memory.verify()}
    finally:memory.close()
