"""Source-bound, integrity-checked geometric tracker snapshots.

Hashes detect damage and mismatched inputs; they do not authenticate a caller.
Filesystem grants remain the responsibility of the integration adapter.
"""
from copy import deepcopy
from pathlib import Path
import math
import re
from seye.core.storage import checksum, atomic_json, read_json
from seye.video.continuity import ContinuityTracker
from seye.video.temporal import frame_contract, finite


def source_digest(value):
    if not isinstance(value,str) or re.fullmatch('[0-9a-f]{64}',value) is None:
        raise ValueError('Lowercase SHA-256 source identity required')
    return value


def snapshot(tracker, source_sha256):
    source_digest(source_sha256)
    if tracker.frame_count<1:raise ValueError('At least one processed frame required')
    payload={'schema_version':1,'kind':'conservative_geometric_tracker','source_sha256':source_sha256,
             'config':{'iou_threshold':tracker.threshold,'max_missed':tracker.max_missed,
                       'max_tracks':tracker.max_tracks,'session_id':tracker.session_id,
                       'max_gap_seconds':tracker.max_gap_seconds},
             'state':{'next_id':tracker.next_id,'last_timestamp':tracker.last_timestamp,
                      'size':tracker.size,'frame_count':tracker.frame_count,
                      'tracks':[dict(track_id=tid,**deepcopy(row)) for tid,row in sorted(tracker.tracks.items())]}}
    # Round-trip validation also prevents exporting manually corrupted objects.
    value={'payload':payload,'sha256':checksum(payload)}
    restore(value,source_sha256)
    return value


def restore(value, expected_source_sha256):
    source_digest(expected_source_sha256)
    if not isinstance(value,dict) or set(value)!={'payload','sha256'}:raise ValueError('Tracker envelope required')
    p=value['payload']
    if not isinstance(p,dict) or checksum(p)!=value['sha256']:raise ValueError('Tracker checksum mismatch')
    if set(p)!={'schema_version','kind','source_sha256','config','state'} or type(p['schema_version']) is not int or p['schema_version']!=1 or p['kind']!='conservative_geometric_tracker':
        raise ValueError('Unsupported tracker schema')
    if p['source_sha256']!=expected_source_sha256:raise ValueError('Tracker source identity mismatch')
    config=p['config']
    if not isinstance(config,dict) or set(config)!={'iou_threshold','max_missed','max_tracks','session_id','max_gap_seconds'}:raise ValueError('Invalid tracker configuration')
    tracker=ContinuityTracker(**config);s=p['state']
    if not isinstance(s,dict) or set(s)!={'next_id','last_timestamp','size','frame_count','tracks'}:raise ValueError('Invalid tracker state')
    for name,lo,hi in (('frame_count',1,300),('next_id',1,19201)):
        if type(s[name]) is not int or not lo<=s[name]<=hi:raise ValueError('Invalid tracker counter')
    frame_contract([],s['last_timestamp'],s['size'])
    if not isinstance(s['tracks'],list) or len(s['tracks'])>tracker.max_tracks:raise ValueError('Invalid track count')
    tracks={}
    for row in s['tracks']:
        if not isinstance(row,dict):raise ValueError('Invalid track state')
        required={'track_id','class','box','velocity','first_seen','last_seen','missed'}
        if not required<=set(row) or set(row)-required-{'unobserved_reason'}:raise ValueError('Unknown track fields')
        tid=row['track_id']
        if type(tid) is not int or not 1<=tid<s['next_id'] or tid in tracks:raise ValueError('Invalid/repeated track id')
        frame_contract([row],s['last_timestamp'],s['size'])
        for name in ('first_seen','last_seen'):finite(row[name],name)
        if not row['first_seen']<=row['last_seen']<=s['last_timestamp']:raise ValueError('Invalid track times')
        if type(row['missed']) is not int or not 0<=row['missed']<=tracker.max_missed or row['missed']>=s['frame_count']:raise ValueError('Invalid missed count')
        if row['missed']==0 and row['last_seen']!=s['last_timestamp']:raise ValueError('Visible time mismatch')
        if row['missed'] and row['last_seen']>=s['last_timestamp']:raise ValueError('Unobserved time mismatch')
        if row.get('unobserved_reason') not in (None,'not_detected','ambiguous_candidates','possible_covering_observation'):raise ValueError('Invalid absence reason')
        if row['missed'] and row.get('unobserved_reason') is None:raise ValueError('Unobserved reason required')
        if not isinstance(row['velocity'],list) or len(row['velocity'])!=2 or any(type(v) not in (int,float) or (not math.isfinite(v) or abs(v)>4_096_000_000) for v in row['velocity']):raise ValueError('Invalid track velocity')
        tracks[tid]={key:deepcopy(v) for key,v in row.items() if key!='track_id'}
    if s['next_id']>s['frame_count']*64+1:raise ValueError('Impossible track counter')
    tracker.tracks=tracks;tracker.next_id=s['next_id'];tracker.last_timestamp=s['last_timestamp']
    tracker.size=list(s['size']);tracker.frame_count=s['frame_count']
    return tracker


def save(path, tracker, source_sha256, allowed_root):
    target=Path(path).resolve();root=Path(allowed_root).resolve()
    if not target.is_relative_to(root):raise PermissionError('Checkpoint outside granted root')
    atomic_json(target,snapshot(tracker,source_sha256))
    return {'sha256':checksum(read_json(target,max_bytes=1024*1024)), 'frames':tracker.frame_count}


def load(path, expected_source_sha256, allowed_root):
    target=Path(path).resolve()
    if not target.is_relative_to(Path(allowed_root).resolve()):raise PermissionError('Checkpoint outside granted root')
    return restore(read_json(target,max_bytes=1024*1024),expected_source_sha256)
