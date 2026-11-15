"""Versioned Python entry point for explicitly granted S-Eye requests.

The default worker is killable. Inline mode is an explicit trusted-caller choice
and has no enforced execution deadline. This is an API, not an OS sandbox.
"""
import json,math
from pathlib import Path
from seye.core.storage import canonical
from seye.integration.service import Permissions,handle,bounded_handle

from seye.integration.contracts import ACTIONS,validate_request,validate_response


def capabilities():
    return {'schema_version':1,'python_api_version':'seye-request-v1','actions':sorted(ACTIONS),
            'default_worker':'killable spawned process','default_filesystem_grants':[],
            'automatic_actions':False,'semantic_identity_proven':False,'v1_release':False,
            'scope':'read/compute by default; persistence/training/video require explicit grants; no shell/network/camera action'}


class Client:
    def __init__(self,permissions=None,timeout=30,isolated=True,strict=False):
        permissions=Permissions() if permissions is None else permissions
        if not isinstance(permissions,Permissions) or type(isolated) is not bool or type(strict) is not bool:raise ValueError('Permissions object and boolean isolation required')
        if type(timeout) not in (int,float) or not math.isfinite(timeout) or not 0<timeout<=120:raise ValueError('Timeout must be in (0,120]')
        for flag in (permissions.memory,permissions.training,permissions.video):
            if type(flag) is not bool:raise ValueError('Permission capabilities must be booleans')
        roots=[]
        for group in (permissions.read_roots,permissions.write_roots):
            if not isinstance(group,(tuple,list)) or len(group)>32:raise ValueError('At most 32 explicit roots per grant required')
            roots.append(tuple(str(Path(root).expanduser().resolve()) for root in group))
        self.permissions=Permissions(*roots,permissions.memory,permissions.training,permissions.video)
        self.timeout,self.isolated,self.strict=timeout,isolated,strict

    def request(self,request):
        validate_request(request,self.strict)
        identifier=request['request_id']
        encoded=canonical(request)
        if len(encoded)>1024*1024:raise ValueError('Request exceeds 1 MiB')
        copied=json.loads(encoded)
        response=bounded_handle(copied,self.permissions,self.timeout) if self.isolated else handle(copied,self.permissions)
        if len(canonical(response))>16*1024*1024:
            return {'schema_version':1,'request_id':identifier,'success':False,'error':{'type':'ResponseLimit','message':'Response exceeds 16 MiB'}}
        return validate_response(response,identifier)

    def call(self,action,request_id,**fields):
        if set(fields)&{'schema_version','request_id','action'}:raise ValueError('Reserved request fields cannot be overridden')
        return self.request(dict(fields,schema_version=1,request_id=request_id,action=action))
