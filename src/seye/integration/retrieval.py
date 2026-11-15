"""Feature-distance evidence with explicit cutoff, self-exclusion and ambiguity."""
import math
from seye.integration.observations import capture
from seye.recognition.pipeline import FeaturePipeline
from seye.memory.packet_index import query


def find(memory,path,maximum_distance,components=('shape',),limit=5,include_self=False,exclude_sources=(),expected_source_sha256=None):
    if type(maximum_distance) not in (int,float) or not math.isfinite(maximum_distance) or not 0<=maximum_distance<=1e6:raise ValueError('Explicit finite nonnegative feature-distance cutoff required')
    if type(include_self) is not bool or type(limit) is not int or not 1<=limit<=20:raise ValueError('Boolean self policy and limit 1..20 required')
    if not isinstance(exclude_sources,(tuple,list)) or len(exclude_sources)>98:raise ValueError('At most 98 source exclusions supported')
    image,source=capture(path,expected_source_sha256);packet=FeaturePipeline().extract(image,components)
    excluded=list(exclude_sources)
    if not include_self:excluded+=list(dict.fromkeys((source['sha256'],source['pixel_sha256'])))
    result=query(memory,packet,limit,excluded,maximum_distance)
    status='no_match' if not result['matches'] else ('ambiguous' if result['ambiguous_top_distance'] else 'feature_candidate')
    return {'status':status,'query_source':source,'schema_sha256':packet['schema_sha256'],'maximum_distance':maximum_distance,
            'self_sources_excluded':not include_self,'evidence':result,'unique_semantic_identity':False,
            'automatic_action_authorized':False,'scope':'feature similarity under caller cutoff, not calibrated confidence or verified object identity'}
