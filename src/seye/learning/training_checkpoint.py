"""Exclusive verified inference checkpoints; no claim of optimizer-state resume."""
from seye.core.storage import atomic_json,read_json,checksum
from seye.learning.packet_linear import validate


def save(path,model):
    validate(model)
    payload={'format':'seye-training-checkpoint-v1','model':model,'scope':'selected inference weights and training history; not mid-optimizer resume'}
    return atomic_json(path,{'payload':payload,'sha256':checksum(payload)})


def load(path):
    envelope=read_json(path);payload=envelope.get('payload')
    if not isinstance(payload,dict) or envelope.get('sha256')!=checksum(payload) or payload.get('format')!='seye-training-checkpoint-v1':raise ValueError('Training checkpoint integrity/format mismatch')
    model=validate(payload['model'])
    history=model.get('history');epochs=model.get('epochs');best=model.get('best_epoch')
    if type(epochs) is not int or not 1<=epochs<=300 or type(best) is not int or not 1<=best<=epochs or not isinstance(history,list) or len(history)!=epochs:raise ValueError('Checkpoint training metadata mismatch')
    return model
