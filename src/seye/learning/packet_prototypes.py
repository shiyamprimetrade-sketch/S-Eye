"""Independent category means bound to exact modular feature schemas and split provenance."""
from copy import deepcopy
import math
from seye.core.storage import checksum,atomic_json,read_json
from seye.recognition.similarity import validate_packet,compare
UNKNOWN='__unknown__'


def validate_records(records):
    if not isinstance(records,list) or not 1<=len(records)<=10000:raise ValueError('1..10000 records required')
    ids=set();contents=set()
    for row in records:
        if not isinstance(row,dict):raise ValueError('Sample object required')
        for field in ('id','group','label'):
            if not isinstance(row.get(field),str) or not 1<=len(row[field])<=128:raise ValueError('Bounded identity, group and label required')
        digest=row.get('content_sha256')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('Canonical source-content identity required')
        if row['id'] in ids or digest in contents:raise ValueError('Duplicate sample or content identity')
        ids.add(row['id']);contents.add(digest);validate_packet(row['packet'])
    schemas={row['packet']['schema_sha256'] for row in records}
    if len(schemas)!=1:raise ValueError('Mixed feature schemas')
    return records


def records_digest(records):return checksum(sorted(records,key=lambda r:r['id']))


def fit(training,validation):
    validate_records(training);validate_records(validation)
    if training[0]['packet']['schema_sha256']!=validation[0]['packet']['schema_sha256']:raise ValueError('Train/validation schema mismatch')
    for key in ('id','group','content_sha256'):
        if {r[key] for r in training}&{r[key] for r in validation}:raise ValueError('Train/validation leakage: '+key)
    labels=sorted({r['label'] for r in training})
    if not 2<=len(labels)<=128 or UNKNOWN in labels:raise ValueError('At least two known classes required')
    if any(r['label'] not in labels+[UNKNOWN] for r in validation):raise ValueError('Unrecognized validation category')
    prototypes={};radii={};counts={}
    for label in labels:
        members=[r['packet']['features'] for r in training if r['label']==label]
        packet=deepcopy(training[0]['packet']);packet['features']=[sum(values[i] for values in members)/len(members) for i in range(len(members[0]))]
        heldout=[r for r in validation if r['label']==label]
        if not heldout:raise ValueError('Known class missing validation')
        prototypes[label]=packet;radii[label]=max(.015,max(compare(r['packet'],packet)['distance'] for r in heldout)*1.1);counts[label]=len(members)
    model={'kind':'seye-packet-prototypes-v1','classes':labels,'prototypes':prototypes,'radii':radii,'training_counts':counts,
           'schema_sha256':training[0]['packet']['schema_sha256'],'training_sha256':records_digest(training),
           'validation_sha256':records_digest(validation),'training_identities':[{k:r[k] for k in ('id','group','content_sha256')} for r in training],
           'validation_identities':[{k:r[k] for k in ('id','group','content_sha256')} for r in validation],
           'pretrained_weights_used':False,'probability_calibrated':False}
    return validate_model(model)


def validate_model(model):
    if not isinstance(model,dict) or model.get('kind')!='seye-packet-prototypes-v1':raise ValueError('Packet prototype model required')
    labels=model.get('classes')
    if not isinstance(labels,list) or not 2<=len(labels)<=128 or any(not isinstance(n,str) or not n or n==UNKNOWN for n in labels) or len(set(labels))!=len(labels):raise ValueError('Invalid model labels')
    for key in ('prototypes','radii','training_counts'):
        if not isinstance(model.get(key),dict) or set(model[key])!=set(labels):raise ValueError('Class inventory mismatch')
    for name in labels:
        validate_packet(model['prototypes'][name])
        if model['prototypes'][name]['schema_sha256']!=model.get('schema_sha256'):raise ValueError('Prototype schema mismatch')
        r=model['radii'][name]
        if type(r) not in (int,float) or not math.isfinite(r) or not 0<r<=1e6:raise ValueError('Invalid radius')
        if type(model['training_counts'][name]) is not int or model['training_counts'][name]<=0:raise ValueError('Invalid support count')
    return model


def nearest(model,packet):
    validate_model(model);validate_packet(packet)
    if packet['schema_sha256']!=model['schema_sha256']:raise ValueError('Inference schema mismatch')
    return sorted([{'label':label,'distance':compare(packet,model['prototypes'][label])['distance'],
                    'radius':model['radii'][label],'training_samples':model['training_counts'][label]} for label in model['classes']],key=lambda r:(r['distance'],r['label']))


def save(path,model):
    validate_model(model);return atomic_json(path,{'model':model,'sha256':checksum(model)})


def load(path):
    envelope=read_json(path)
    if checksum(envelope['model'])!=envelope.get('sha256'):raise ValueError('Packet checkpoint integrity mismatch')
    return validate_model(envelope['model'])
