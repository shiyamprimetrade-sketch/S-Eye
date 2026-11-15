"""Finite version-1 JSON contracts; schema data never selects executable code."""
import json,math
from seye.core.storage import canonical

# Required and optional top-level fields. Legacy direct service callers retain
# their existing permissive argument handling; strict validation is opt-in.
CONTRACTS={
 'analyze':('image','mode'), 'recognize':('image model',''),
 'visual_question':('image question','mode'), 'remember':('image memory','mode'), 'retrieve':('image memory','limit'),
 'track_sequence':('samples source_sha256','config checkpoint output_checkpoint'),
 'interface_video':('video','fps max_seconds tracking_mode'),
 'observe_interface':('image','previous templates stride min_similarity matcher scales region_proposals region_mode memory memory_components'),
 'observe_interface_batch':('images','options'),
 'profile_interface':('image','previous templates stride min_similarity matcher scales region_proposals region_mode'),
 'extract_features':('image','components perspective_quad canonical_size'),
 'extract_feature_sets':('image selections',''), 'extract_feature_batch':('images','components'),
 'recognize_packet':('image model','calibration top_k min_margin'), 'recognize_trained':('image model','memory'),
 'memory_index_build':('memory',''), 'memory_packet_query':('memory image','components limit exclude_sources maximum_distance'),
 'memory_packet_query_many':('memory packets','limit exclude_sources maximum_distance'),
 'memory_history_link':('memory entity observation_id session event_index','reason'), 'memory_history':('memory entity','limit'),
 'memory_inspect':('memory observation_id',''), 'memory_provenance':('memory',''), 'memory_duplicates':('memory',''),
 'memory_compare':('memory before after',''), 'memory_scene_inventory':('memory observation_id',''),
 'memory_bundle_export':('memory output',''), 'memory_bundle_restore':('memory bundle',''),
 'memory_retention_plan':('memory maximum','protected'), 'memory_retention_apply':('memory plan',''),
 'memory_storage':('memory',''), 'memory_snapshot':('memory output','backup_timeout'),
 'scene_analyze':('memory observation_id',''), 'scene_compare':('memory before after','normalize'),
 'scene_changes':('memory before after','registration movement_tolerance'),
 'scene_absence':('memory reference observations','minimum_consecutive'),
 'recognize_batch':('images model',''), 'memory_list':('memory','limit'),
 'train':('manifest output','method'), 'video':('video','fps max_seconds mode'),
 'memory_store_image':('memory image','components expected_source_sha256'),
 'memory_get_observation':('memory observation_id',''),
 'image_observe':('image','expected_source_sha256 options'),
 'memory_find':('memory image maximum_distance','components limit include_self exclude_sources'),
 'ask_observation':('image question','previous expected_source_sha256'),
 # EXTENSIONS
}
ACTIONS=frozenset(CONTRACTS)
ENVELOPE={'schema_version','request_id','action'}


def json_value(value,maximum=1024*1024):
    nodes=0;strings=0;node_budget=100000 if maximum<=1024*1024 else 1000000
    def visit(item,depth):
        nonlocal nodes,strings
        nodes+=1
        if nodes>node_budget or depth>32:raise ValueError('JSON depth/node budget exceeded')
        if type(item) is dict:
            for key,child in item.items():
                if not isinstance(key,str):raise ValueError('JSON keys must be strings')
                visit(key,depth+1);visit(child,depth+1)
        elif type(item) is list:
            for child in item:visit(child,depth+1)
        elif type(item) is str:
            strings+=len(item.encode('utf-8'))
            if strings>maximum:raise ValueError('JSON string byte budget exceeded')
        elif type(item) is float:
            if not math.isfinite(item):raise ValueError('Finite JSON numbers required')
        elif type(item) not in (int,bool,type(None)):raise ValueError('JSON primitives required')
    visit(value,0);raw=canonical(value)
    if len(raw)>maximum:raise ValueError('JSON byte budget exceeded')
    return raw


def validate_request(request,strict=False):
    if type(strict) is not bool:raise ValueError('Boolean strict flag required')
    if not isinstance(request,dict) or type(request.get('schema_version')) is not int or request['schema_version']!=1:raise ValueError('Request schema_version=1 required')
    identifier=request.get('request_id');action=request.get('action')
    if not isinstance(identifier,str) or not 1<=len(identifier)<=128 or not isinstance(action,str) or action not in ACTIONS:raise ValueError('Bounded request ID and supported action required')
    required,optional=CONTRACTS[action];missing=set(required.split())-set(request)
    if missing:raise ValueError('Missing action fields: '+','.join(sorted(missing)))
    if strict and set(request)-ENVELOPE-set(required.split())-set(optional.split()):raise ValueError('Unknown action fields')
    json_value(request)
    return request


def validate_response(response,request_id):
    if not isinstance(response,dict) or type(response.get('schema_version')) is not int or response['schema_version']!=1 or response.get('request_id')!=request_id or type(response.get('success')) is not bool:raise ValueError('Response envelope/identity mismatch')
    if response['success']:
        if 'result' not in response or 'error' in response:raise ValueError('Success requires result without error')
    else:
        error=response.get('error')
        if 'result' in response or not isinstance(error,dict) or not all(isinstance(error.get(k),str) and error[k] for k in ('type','message')):raise ValueError('Failure requires typed error without result')
    json_value(response,16*1024*1024)
    return response


def describe():
    return {'format':'seye-action-contract-v1','schema_version':1,'request_envelope':sorted(ENVELOPE),
            'actions':{name:{'required':r.split(),'optional':o.split()} for name,(r,o) in sorted(CONTRACTS.items())},
            'max_request_bytes':1024*1024,'max_response_bytes':16*1024*1024,'max_depth':32,
            'scope':'structural contracts; action-specific limits and explicit filesystem/capability grants still apply'}


def decode_request(raw,strict=False):
    if not isinstance(raw,bytes) or len(raw)>1024*1024:raise ValueError('Bounded UTF-8 request bytes required')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate JSON field')
            result[key]=value
        return result
    request=json.loads(raw,object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    return validate_request(request,strict)
