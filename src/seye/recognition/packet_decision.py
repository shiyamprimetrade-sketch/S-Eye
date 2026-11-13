"""Known-radius rejection and explicit ambiguity for schema-bound prototypes."""
import math
from seye.learning.packet_prototypes import nearest,UNKNOWN


def decide(model,packet,min_margin=.005):
    if type(min_margin) not in (int,float) or not math.isfinite(min_margin) or not 0<=min_margin<=1:raise ValueError('Margin must be in [0,1]')
    candidates=nearest(model,packet);first,second=candidates[:2]
    gap=second['distance']-first['distance']
    if first['distance']>first['radius']:accepted=False;reason='outside_validation_radius'
    elif gap<=min_margin:accepted=False;reason='ambiguous_known_categories'
    else:accepted=True;reason='nearest_within_validation_radius'
    return {'label':first['label'] if accepted else UNKNOWN,'accepted':accepted,'reason':reason,
            'nearest_distance':first['distance'],'rejection_radius':first['radius'],'candidate_margin':gap,
            'minimum_margin':min_margin,'confidence_probability':None}


def candidates(model,packet,top_k=3,min_margin=.005):
    if type(top_k) is not int or not 1<=top_k<=10:raise ValueError('top_k must be in [1,10]')
    ranked=nearest(model,packet);selection=decide(model,packet,min_margin)
    return {'selection':selection,'candidates':[dict(r,within_radius=r['distance']<=r['radius'],
            label_origin='training_records') for r in ranked[:top_k]],
            'total_candidates':len(ranked),'truncated':len(ranked)>top_k,'confidence_probability':None}
