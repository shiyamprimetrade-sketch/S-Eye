"""Explicit config inspection/migration/export, never an in-place permission edit."""
from seye.core.configuration import load_config,parse_config
from seye.core.storage import atomic_json,checksum
from seye.local.workspace import inside


def serialize(parsed):
    p=parsed['permissions']
    return {'schema_version':1,'read_roots':list(p.read_roots),'write_roots':list(p.write_roots),
            'memory':p.memory,'training':p.training,'video':p.video,'timeout':parsed['timeout']}


def inspect(path,allowed_root):
    parsed=load_config(inside(path,allowed_root));data=serialize(parsed)
    return {'format':'seye-config-inspection-v1','source_version':parsed['source_version'],'normalized':data,
            'normalized_sha256':checksum(data),'applied':False}


def initialize(root,destination,allowed_root,allow_write=False,allow_memory=False,timeout=30):
    root=inside(root,allowed_root);destination=inside(destination,allowed_root)
    if type(allow_write) is not bool or type(allow_memory) is not bool:raise ValueError('Explicit boolean capability choices required')
    data=serialize(parse_config({'schema_version':1,'read_roots':[str(root)],'write_roots':[str(root)] if allow_write else [],
                                 'memory':allow_memory,'training':False,'video':False,'timeout':timeout}))
    atomic_json(destination,data)
    return {'config_sha256':checksum(data),'source_version':1,'applied':False}


def migrate(source,destination,allowed_root):
    source=inside(source,allowed_root);destination=inside(destination,allowed_root)
    parsed=load_config(source);data=serialize(parsed)
    # Pure normalization is checked again before exclusive publication.
    if serialize(parse_config(data))!=data:raise ValueError('Configuration migration did not preserve normalized permissions')
    atomic_json(destination,data)
    return {'from_version':parsed['source_version'],'to_version':1,'config_sha256':checksum(data),'in_place':False,'applied':False}


def difference(before,after):
    left=serialize(before);right=serialize(after)
    return {'added_read_roots':sorted(set(right['read_roots'])-set(left['read_roots'])),
            'added_write_roots':sorted(set(right['write_roots'])-set(left['write_roots'])),
            'removed_read_roots':sorted(set(left['read_roots'])-set(right['read_roots'])),
            'removed_write_roots':sorted(set(left['write_roots'])-set(right['write_roots'])),
            'enabled_capabilities':[k for k in ('memory','training','video') if right[k] and not left[k]],
            'disabled_capabilities':[k for k in ('memory','training','video') if left[k] and not right[k]],'applied':False}
