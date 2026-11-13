"""Conservative bounded geometric tracking, independent of the legacy tracker.

Only isolated candidate edges are accepted. Ambiguous observations are retained
as unresolved evidence rather than forcing a semantic identity decision.
"""
from copy import deepcopy
import re
import uuid
from seye.detection.metrics import box_iou
from seye.video.temporal import finite, frame_contract
from seye.video.motion import motion


class ContinuityTracker:
    def __init__(self, iou_threshold=.2, max_missed=2, max_tracks=64, session_id=None, max_gap_seconds=2):
        finite(iou_threshold,'iou_threshold')
        if not 0<iou_threshold<=1: raise ValueError('IoU threshold in (0,1] required')
        if type(max_missed) is not int or not 0<=max_missed<=30: raise ValueError('max_missed in 0..30 required')
        if type(max_tracks) is not int or not 1<=max_tracks<=64: raise ValueError('max_tracks in 1..64 required')
        session_id=uuid.uuid4().hex if session_id is None else session_id
        if not isinstance(session_id,str) or re.fullmatch(r'[A-Za-z0-9_-]{1,64}',session_id) is None:
            raise ValueError('Bounded session identifier required')
        finite(max_gap_seconds,'max_gap_seconds')
        if not 0<max_gap_seconds<=30:raise ValueError('max_gap_seconds in (0,30] required')
        self.session_id,self.max_gap_seconds=session_id,max_gap_seconds
        self.threshold,self.max_missed,self.max_tracks=iou_threshold,max_missed,max_tracks
        self.tracks={};self.next_id=1;self.last_timestamp=None;self.size=None;self.frame_count=0

    def update(self, detections, timestamp, size, discontinuity=False):
        clean=frame_contract(detections,timestamp,size,self.last_timestamp)
        if type(discontinuity) is not bool:raise ValueError('Explicit boolean discontinuity required')
        if self.size is not None and list(size)!=self.size and not discontinuity:
            raise ValueError('Decoded grid changed; start a new tracker')
        tracks=deepcopy(self.tracks);next_id=self.next_id
        expired=[tid for tid,tr in sorted(tracks.items()) if discontinuity or timestamp-tr['last_seen']>self.max_gap_seconds]
        retirements=[{'track_id':tid,'reason':'caller_discontinuity' if discontinuity else 'elapsed_gap_limit'} for tid in expired]
        for tid in expired:del tracks[tid]
        candidates=[]
        for identifier,track in sorted(tracks.items()):
            dt=timestamp-track['last_seen']
            shift=[v*dt for v in track['velocity']]
            expected=[v+shift[i%2] for i,v in enumerate(track['box'])]
            for index,row in enumerate(clean):
                score=box_iou(expected,row['box']) if track['class']==row['class'] else 0
                if score>=self.threshold:
                    candidates.append({'track_id':identifier,'detection_index':index,'predicted_iou':score})
        track_degree={};detection_degree={}
        for edge in candidates:
            tid,index=edge['track_id'],edge['detection_index']
            track_degree[tid]=track_degree.get(tid,0)+1
            detection_degree[index]=detection_degree.get(index,0)+1
        accepted=[edge for edge in candidates if track_degree[edge['track_id']]==1 and detection_degree[edge['detection_index']]==1]
        visible=[];matched=set();used=set()
        for edge in accepted:
            tid,index=edge['track_id'],edge['detection_index'];track=tracks[tid];row=clean[index]
            evidence=motion(track['box'],row['box'],timestamp-track['last_seen'])
            track.update(box=list(row['box']),velocity=evidence['velocity'],last_seen=timestamp,missed=0)
            visible.append({'track_id':tid,**deepcopy(row),'motion':evidence,'association':'isolated_geometric_candidate'})
            matched.add(tid);used.add(index)
        retired=[]
        for tid in sorted(tracks):
            if tid not in matched:
                tracks[tid]['missed']+=1
                if tracks[tid]['missed']>self.max_missed:
                    retired.append(tid)
        for tid in retired:
            retirements.append({'track_id':tid,'reason':'missed_frame_limit'})
            del tracks[tid]
        unresolved=[i for i in range(len(clean)) if i not in used and i in detection_degree]
        births=[i for i in range(len(clean)) if i not in used and i not in detection_degree]
        if len(tracks)+len(births)>self.max_tracks:raise ValueError('Active track capacity exceeded')
        for index in sorted(births,key=lambda i:(clean[i]['class'],clean[i]['box'])):
            row=clean[index];tid=next_id;next_id+=1
            tracks[tid]={'class':row['class'],'box':list(row['box']),'velocity':[0.,0.],
                         'first_seen':timestamp,'last_seen':timestamp,'missed':0}
            visible.append({'track_id':tid,**deepcopy(row),'motion':None,'association':'new_geometric_track'})
        result={'timestamp':timestamp,'frame_index':self.frame_count,'source_size':list(size),
                'visible':sorted(visible,key=lambda r:r['track_id']),
                'unresolved_detection_indices':unresolved,'candidate_edges':candidates,
                'retained_unobserved_ids':sorted(set(tracks)-{r['track_id'] for r in visible}),
                'retired_ids':sorted(expired+retired),'retirements':retirements,
                'session_id':self.session_id,'caller_discontinuity':discontinuity,'semantic_identity_proven':False,'automatic_action_authorized':False}
        for row in result['visible']:
            row['track_uid']=f"{self.session_id}:{row['track_id']}"
        self.tracks,self.next_id,self.last_timestamp,self.size=tracks,next_id,timestamp,list(size)
        self.frame_count+=1
        return result
