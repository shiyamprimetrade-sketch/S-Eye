"""Bounded frame-local spatial evidence, without semantic identities or registration."""
import math
from seye.detection.metrics import box_iou


def frame(value):
    if not isinstance(value,dict) or not isinstance(value.get('objects'),list) or len(value['objects'])>128:raise ValueError('Frame requires at most 128 visual hypotheses')
    size=value.get('source_size')
    if size is not None and (not isinstance(size,(list,tuple)) or len(size)!=2 or any(type(v) is not int or not 0<v<=20_000_000 for v in size) or size[0]*size[1]>20_000_000):raise ValueError('Bounded source dimensions required')
    for obj in value['objects']:
        if not isinstance(obj,dict):raise ValueError('Visual hypothesis object required')
        box=obj.get('box')
        if not isinstance(box,(list,tuple)) or len(box)!=4 or any(type(v) not in (int,float) or abs(v)>20_000_000 or not math.isfinite(v) for v in box) or box[2]<=box[0] or box[3]<=box[1]:raise ValueError('Finite bounded half-open box required')
        if size is not None and not (0<=box[0]<box[2]<=size[0] and 0<=box[1]<box[3]<=size[1]):raise ValueError('Box outside source grid')
        if not isinstance(obj.get('class','unknown'),str) or not 1<=len(obj.get('class','unknown'))<=128:raise ValueError('Bounded class hypothesis required')
    return value


def relationships(value):
    frame(value);rows=value['objects'];pairs=[]
    for i,a in enumerate(rows):
        for j in range(i+1,len(rows)):
            x,y=a['box'],rows[j]['box'];overlap=box_iou(x,y)
            gap_x=max(0,x[0]-y[2],y[0]-x[2]);gap_y=max(0,x[1]-y[3],y[1]-x[3])
            contains=x[0]<=y[0] and x[1]<=y[1] and x[2]>=y[2] and x[3]>=y[3]
            inside=y[0]<=x[0] and y[1]<=x[1] and y[2]>=x[2] and y[3]>=x[3]
            topology='same_bounds' if contains and inside else 'first_contains_second' if contains else 'second_contains_first' if inside else 'overlap' if overlap>0 else 'touching' if gap_x==gap_y==0 else 'disjoint'
            horizontal='first_left_disjoint' if x[2]<=y[0] else 'first_right_disjoint' if y[2]<=x[0] else 'horizontal_overlap'
            vertical='first_above_disjoint' if x[3]<=y[1] else 'first_below_disjoint' if y[3]<=x[1] else 'vertical_overlap'
            pairs.append({'first':i,'second':j,'topology':topology,'horizontal':horizontal,'vertical':vertical,
                          'box_iou':overlap,'edge_gap_pixels':[gap_x,gap_y]})
    return {'objects':len(rows),'relations':pairs,'identity_scope':'frame-local geometric evidence, not persistent or semantic identity'}
