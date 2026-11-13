"""Immutable dataset revisions with source/pixel identities and existing leakage audits."""
import re
from pathlib import Path
from seye.core.storage import checksum,read_json,atomic_json
from seye.core.datasets import validate_splits,fingerprint,POLICY
from seye.image.ingestion import load_image


def validate_snapshot(snapshot):
    if not isinstance(snapshot,dict) or not isinstance(snapshot.get('payload'),dict) or snapshot.get('sha256')!=checksum(snapshot['payload']):raise ValueError('Dataset revision integrity mismatch')
    p=snapshot['payload']
    if p.get('schema')!='seye-dataset-revision-v1' or not isinstance(p.get('images'),list) or not 1<=len(p['images'])<=2000:raise ValueError('Invalid dataset revision schema')
    if not isinstance(p.get('dataset_id'),str) or not p['dataset_id'] or not isinstance(p.get('version'),str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)',p['version']):raise ValueError('Invalid dataset revision identity/version')
    if any(not isinstance(row,dict) for row in p['images']):raise ValueError('Dataset image objects required')
    return snapshot


def snapshot(manifest,version,parent=None):
    manifest=Path(manifest).resolve();data=read_json(manifest)
    if not isinstance(version,str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)',version):raise ValueError('Semantic dataset version required')
    if not isinstance(data,dict) or data.get('schema_version')!=1 or not isinstance(data.get('dataset_id'),str) or not data['dataset_id'] or not isinstance(data.get('images'),list) or not 1<=len(data['images'])<=2000:raise ValueError('Bounded versioned dataset manifest required')
    if parent is not None:
        validate_snapshot(parent)
        if parent['payload']['dataset_id']!=data['dataset_id'] or tuple(map(int,version.split('.'))) <= tuple(map(int,parent['payload']['version'].split('.'))):raise ValueError('Dataset parent or monotonic version mismatch')
    rows=[];pixels=set()
    for row in data['images']:
        if not isinstance(row,dict):raise ValueError('Dataset image object required')
        if row.get('split') not in ('train','validation','test') or not isinstance(row.get('label'),str) or not row['label'] or row.get('source_kind') not in ('synthetic','photograph','screenshot') or row.get('annotation_status') not in ('generator','draft','human_reviewed'):raise ValueError('Split, label and annotation provenance required')
        if not isinstance(row.get('path'),str):raise ValueError('Source path required')
        path=(manifest.parent/row['path']).resolve();_,source=load_image(path,allowed_root=manifest.parent)
        if source['sha256']!=row.get('sha256'):raise ValueError('Dataset source changed')
        pixel=fingerprint(path)['pixel_sha256']
        if pixel in pixels:raise ValueError('Duplicate decoded source pixels')
        pixels.add(pixel);rows.append(dict(row,pixel_sha256=pixel))
    validate_splits(rows,manifest.parent)
    payload={'schema':'seye-dataset-revision-v1','dataset_id':data['dataset_id'],'version':version,
             'parent_sha256':parent['sha256'] if parent is not None else None,'images':sorted(rows,key=lambda r:r['id']),
             'leakage_policy':POLICY,'scope':'source identity and heuristic leakage audit; annotation truth and scene independence are not certified'}
    return {'payload':payload,'sha256':checksum(payload)}


def save(path,revision):return atomic_json(path,validate_snapshot(revision))


def verify(revision,directory):
    validate_snapshot(revision);root=Path(directory).resolve()
    for row in revision['payload']['images']:
        path=(root/row['path']).resolve();_,source=load_image(path,allowed_root=root)
        if source['sha256']!=row['sha256'] or fingerprint(path)['pixel_sha256']!=row['pixel_sha256']:raise ValueError('Dataset source/pixel identity mismatch')
    validate_splits(revision['payload']['images'],root)
    return {'verified_sources':len(revision['payload']['images']),'revision_sha256':revision['sha256']}


def diff(first,second):
    validate_snapshot(first);validate_snapshot(second)
    a={r['id']:r for r in first['payload']['images']};b={r['id']:r for r in second['payload']['images']}
    return {'added':sorted(b.keys()-a.keys()),'removed':sorted(a.keys()-b.keys()),
            'changed':sorted(k for k in a.keys()&b.keys() if a[k]!=b[k]),
            'labels_changed':sorted(k for k in a.keys()&b.keys() if a[k]['label']!=b[k]['label'])}
