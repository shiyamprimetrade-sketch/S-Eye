"""Movement/size evidence under a common grid and optional caller registration."""
import copy,math
from seye.scenes.spatial import frame
from seye.scenes.comparison import compare_layout


def changes(before,after,registration=None,movement_tolerance=2):
    frame(before);frame(after)
    if type(movement_tolerance) not in (int,float) or not math.isfinite(movement_tolerance) or not 0<=movement_tolerance<=64:raise ValueError('Bounded movement tolerance required')
    registered=copy.deepcopy(before);dx=dy=0.0
    if registration is not None:
        if not isinstance(registration,dict) or set(registration)!={'dx','dy'} or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>4096 for v in registration.values()):raise ValueError('Bounded explicit translation required')
        dx,dy=registration['dx'],registration['dy']
        for obj in registered['objects']:
            x1,y1,x2,y2=obj['box'];obj['box']=[x1+dx,y1+dy,x2+dx,y2+dy]
        # Registration is not permission to clip or infer off-screen objects.
        frame(registered)
    r=compare_layout(registered,after)
    if not r['comparable']:return dict(r,events=[],registration_origin='caller' if registration else 'none')
    events=[]
    for match in r['matches']:
        i,j=match['expected'],match['predicted'];a,b=before['objects'][i]['box'],after['objects'][j]['box']
        movement=[(b[0]+b[2]-a[0]-a[2])/2,(b[1]+b[3]-a[1]-a[3])/2]
        residual=[movement[0]-dx,movement[1]-dy];size_delta=[b[2]-b[0]-(a[2]-a[0]),b[3]-b[1]-(a[3]-a[1])]
        kind='resized' if any(abs(v)>movement_tolerance for v in size_delta) else 'moved' if math.hypot(*residual)>movement_tolerance else 'stable'
        events.append({'before':i,'after':j,'kind':kind,'observed_center_delta':movement,'registered_residual_delta':residual,'size_delta':size_delta,
                       'correspondence_ambiguous':r['ambiguous_correspondence']})
    return dict(r,events=events,registration_origin='caller' if registration is not None else 'none',
                registration=registration,scope='geometric change hypotheses, not proof of semantic object movement or removal')
