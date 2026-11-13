"""Versioned Python entry point for explicitly granted S-Eye requests.

The default worker is killable. Inline mode is an explicit trusted-caller choice
and has no enforced execution deadline. This is an API, not an OS sandbox.
"""
import json,math
from pathlib import Path
from seye.core.storage import canonical
from seye.integration.service import Permissions,handle,bounded_handle

ACTIONS=frozenset(('analyze','recognize','visual_question','remember','retrieve','track_sequence','interface_video',
 'observe_interface','observe_interface_batch','profile_interface','extract_features','extract_feature_sets','extract_feature_batch',
 'recognize_packet','recognize_trained','memory_index_build','memory_packet_query','memory_packet_query_many',
 'memory_history_link','memory_history','memory_inspect','memory_provenance','memory_duplicates','memory_compare','memory_scene_inventory',
 'memory_bundle_export','memory_bundle_restore','memory_retention_plan','memory_retention_apply','memory_storage','memory_snapshot',
 'scene_analyze','scene_compare','scene_changes','scene_absence','recognize_batch','memory_list','train','video'))


def capabilities():
    return {'schema_version':1,'python_api_version':'seye-request-v1','actions':sorted(ACTIONS),
            'default_worker':'killable spawned process','default_filesystem_grants':[],
            'automatic_actions':False,'semantic_identity_proven':False,'v1_release':False,
            'scope':'read/compute by default; persistence/training/video require explicit grants; no shell/network/camera action'}


class Client:
    def __init__(self,permissions=None,timeout=30,isolated=True):
        permissions=Permissions() if permissions is None else permissions
        if not isinstance(permissions,Permissions) or type(isolated) is not bool:raise ValueError('Permissions object and boolean isolation required')
        if type(timeout) not in (int,float) or not math.isfinite(timeout) or not 0<timeout<=120:raise ValueError('Timeout must be in (0,120]')
        for flag in (permissions.memory,permissions.training,permissions.video):
            if type(flag) is not bool:raise ValueError('Permission capabilities must be booleans')
        roots=[]
        for group in (permissions.read_roots,permissions.write_roots):
            if not isinstance(group,(tuple,list)) or len(group)>32:raise ValueError('At most 32 explicit roots per grant required')
            roots.append(tuple(str(Path(root).expanduser().resolve()) for root in group))
        self.permissions=Permissions(*roots,permissions.memory,permissions.training,permissions.video)
        self.timeout,self.isolated=timeout,isolated

    def request(self,request):
        if not isinstance(request,dict) or type(request.get('schema_version')) is not int or request['schema_version']!=1:
            raise ValueError('Request schema_version=1 required')
        identifier=request.get('request_id')
        if not isinstance(identifier,str) or not 1<=len(identifier)<=128 or not isinstance(request.get('action'),str) or request['action'] not in ACTIONS:
            raise ValueError('Bounded request identity and supported action required')
        encoded=canonical(request)
        if len(encoded)>1024*1024:raise ValueError('Request exceeds 1 MiB')
        copied=json.loads(encoded)
        response=bounded_handle(copied,self.permissions,self.timeout) if self.isolated else handle(copied,self.permissions)
        if len(canonical(response))>16*1024*1024:
            return {'schema_version':1,'request_id':identifier,'success':False,'error':{'type':'ResponseLimit','message':'Response exceeds 16 MiB'}}
        return response

    def call(self,action,request_id,**fields):
        if set(fields)&{'schema_version','request_id','action'}:raise ValueError('Reserved request fields cannot be overridden')
        return self.request(dict(fields,schema_version=1,request_id=request_id,action=action))
