"""Bounded evidence summaries; sampled endpoint travel is not continuous motion."""
from math import hypot
from seye.core.storage import checksum
from seye.video.temporal import frame_contract


def summarize(frames, source_sha256):
    from seye.video.checkpoint import source_digest
    source_digest(source_sha256)
    if not isinstance(frames,list) or not 1<=len(frames)<=300:raise ValueError('1..300 sampled frames required')
    tracks={};previous=None;session=None;unresolved=0;retired=set();last_size=None
    for frame in frames:
        if not isinstance(frame,dict):raise ValueError('Frame object required')
        identity=frame.get('session_id')
        if not isinstance(identity,str) or not identity:raise ValueError('Session identity required')
        if session is None:session=identity
        if identity!=session:raise ValueError('Cannot combine unrelated sessions')
        visible=frame.get('visible');timestamp=frame.get('timestamp');size=frame.get('source_size')
        frame_contract(visible,timestamp,size,previous)
        if last_size is not None and list(size)!=last_size and frame.get('caller_discontinuity') is not True:
            raise ValueError('Unregistered grid change')
        previous=timestamp;last_size=list(size);seen=set()
        for row in visible:
            tid=row.get('track_id')
            if type(tid) is not int or tid<1 or tid in seen or tid in retired or row.get('track_uid')!=f'{session}:{tid}':raise ValueError('Invalid/reused track identity')
            seen.add(tid)
            value=tracks.setdefault(tid,{'track_uid':row['track_uid'],'class':row['class'],'first_seen':timestamp,
                                         'last_seen':timestamp,'visible_samples':0,'tentative_reacquisitions':0,
                                         'sampled_endpoint_travel_pixels':0.,'unobserved_samples':0,
                                         'last_box':list(row['box']),'retirement_reason':None})
            if value['class']!=row['class']:raise ValueError('Class changed within a geometric track')
            if value['visible_samples']:
                old=value['last_box'];new=row['box']
                value['sampled_endpoint_travel_pixels']+=hypot(*[((new[i]+new[i+2])-(old[i]+old[i+2]))/2 for i in (0,1)])
            value['visible_samples']+=1;value['last_seen']=timestamp;value['last_box']=list(row['box'])
            value['tentative_reacquisitions']+=row.get('association')=='tentative_reacquisition'
        unobserved=frame.get('unobserved',[])
        if not isinstance(unobserved,list) or len(unobserved)>64:raise ValueError('Bounded unobserved list required')
        hidden=set()
        for row in unobserved:
            tid=row.get('track_id')
            if type(tid) is not int or tid not in tracks or tid in seen or tid in hidden or tid in retired:raise ValueError('Unobserved track lacks valid history')
            hidden.add(tid);tracks[tid]['unobserved_samples']+=1
        events=frame.get('retirements',[])
        if not isinstance(events,list) or len(events)>64:raise ValueError('Bounded retirement list required')
        for event in events:
            tid=event.get('track_id')
            if type(tid) is not int or tid not in tracks or tid in seen or tid in retired:raise ValueError('Invalid retirement')
            if event.get('reason') not in ('caller_discontinuity','elapsed_gap_limit','missed_frame_limit'):raise ValueError('Invalid retirement reason')
            retired.add(tid);tracks[tid]['retirement_reason']=event['reason']
        indices=frame.get('unresolved_detection_indices',[])
        if not isinstance(indices,list) or len(indices)>64 or any(type(i) is not int or not 0<=i<64 for i in indices) or len(indices)!=len(set(indices)):raise ValueError('Invalid unresolved indices')
        unresolved+=len(indices)
    rows=[]
    for tid,value in sorted(tracks.items()):
        value.pop('last_box')
        value['sample_span_seconds']=value['last_seen']-value['first_seen']
        rows.append(value)
    return {'schema_version':1,'kind':'sampled_geometric_track_summary','source_sha256':source_sha256,
            'frames_sha256':checksum(frames),'session_id':session,'sampled_frames':len(frames),'tracks':rows,
            'unresolved_observations':unresolved,'semantic_identity_proven':False,
            'timestamp_scope':'caller-supplied sampling grid; not original PTS',
            'limitations':['Travel sums sampled endpoints, including gaps; actual path and continuous visibility are unknown.',
                           'Track IDs are geometric hypotheses; no UI semantics or action authority.']}
