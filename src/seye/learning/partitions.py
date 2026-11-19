"""Partition guards before fitting; descriptor identity does not certify scene independence."""
from seye.learning.annotations import validate_annotations
from seye.learning.packet_prototypes import UNKNOWN
from seye.core.storage import checksum


def validate_partitions(splits):
    if not isinstance(splits,dict) or set(splits)!= {'train','validation','test'}:raise ValueError('Three explicit partitions required')
    identities={};schemas=set()
    for name,rows in splits.items():
        validate_annotations(rows);schemas.update(r['packet']['schema_sha256'] for r in rows)
        identities[name]={field:{r[field] for r in rows} for field in ('id','group','content_sha256')}
    if len(schemas)!=1:raise ValueError('Partition feature schemas differ')
    names=list(splits)
    for i,name in enumerate(names):
        for other in names[i+1:]:
            for field in ('id','group','content_sha256'):
                if identities[name][field]&identities[other][field]:raise ValueError('Cross-partition leakage: '+field)
    known={r['label'] for r in splits['train']}
    if UNKNOWN in known or len(known)<2:raise ValueError('Known-only training classes required')
    if known-{r['label'] for r in splits['validation']}:raise ValueError('Validation missing known categories')
    if any(r['label'] not in known|{UNKNOWN} for part in ('validation','test') for r in splits[part]):raise ValueError('Unsupported evaluation taxonomy')
    return {'partition_sha256':{name:checksum(sorted(rows,key=lambda r:r['id'])) for name,rows in splits.items()},
            'counts':{name:len(rows) for name,rows in splits.items()},'schema_sha256':next(iter(schemas)),
            'near_duplicate_scene_independence_certified':False,
            'scope':'ID/content/declared group guards only; use source-image audit for near duplicates'}
