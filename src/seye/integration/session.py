"""Explicit observe/store/query/question composition for a future main-S caller."""
import re,math
from seye.api import Client
from seye.integration.memory_adapter import MemoryAdapter
from seye.integration.tools_adapter import manifest as tool_manifest


def integration_requirements():
    return {'format':'seye-main-s-requirements-v1','main_s_registration':'not_deployed','tool_specs':tool_manifest(),
            'required_connections':['trusted captured-image provider','explicit file/capability grants','version-1 JSON caller','caller-owned decision/action layer'],
            'camera_in_seye':False,'automatic_action_authorized':False,
            'scope':'executable adapter/session contract; not proof of main-S installation or UI control'}


class EyeSession:
    def __init__(self,client,session_id,memory=None):
        if not isinstance(client,Client) or not isinstance(session_id,str) or re.fullmatch('[A-Za-z0-9_-]{1,64}',session_id) is None:raise ValueError('Client and bounded session identifier required')
        if memory is not None and (not isinstance(memory,MemoryAdapter) or memory.client is not client):raise ValueError('Memory adapter must share the same explicit Client')
        self.client,self.session_id,self.memory=client,session_id,memory

    def run(self,image,persist=False,maximum_distance=None,include_self=False,question='count_proposed_regions',expected_source_sha256=None):
        if type(persist) is not bool or type(include_self) is not bool:raise ValueError('Explicit boolean workflow policies required')
        if persist and (self.memory is None or not self.memory.writable):raise PermissionError('Workflow persistence needs an explicit writable memory adapter')
        if maximum_distance is not None:
            if type(maximum_distance) not in (int,float) or not math.isfinite(maximum_distance) or not 0<=maximum_distance<=1e6:raise ValueError('Explicit finite nonnegative feature cutoff required')
            if self.memory is None:raise ValueError('Retrieval requires a memory adapter')
        if question is not None and (not isinstance(question,str) or not 1<=len(question)<=256):raise ValueError('Bounded question string required')
        steps=[];writes=[]
        def record(operation,response):
            steps.append({'operation':operation,'response':response})
            if response['success'] and operation in ('store','index'):writes.append(operation)
            return response['success']
        def result(success,source=None):
            return {'schema_version':1,'session_id':self.session_id,'success':success,'source_sha256':source,
                    'steps':steps,'successful_write_steps':list(writes),'automatic_action_authorized':False,
                    'scope':'explicit source-bound workflow; completed writes are not rolled back if a later request fails'}
        prefix=self.session_id
        observed=self.client.call('image_observe',prefix+':observe',image=str(image),expected_source_sha256=expected_source_sha256)
        if not record('observe',observed):return result(False)
        digest=observed['result']['identity']['source_sha256']
        if persist:
            saved=self.memory.store_image(image,prefix+':store',expected_source_sha256=digest)
            if not record('store',saved):return result(False,digest)
            indexed=self.memory.build_index(prefix+':index')
            if not record('index',indexed):return result(False,digest)
        if maximum_distance is not None:
            found=self.memory.find(image,prefix+':find',maximum_distance,include_self=include_self,expected_source_sha256=digest)
            if not record('find',found):return result(False,digest)
        if question is not None:
            answer=self.client.call('ask_observation',prefix+':question',image=str(image),question=question,expected_source_sha256=digest)
            if not record('question',answer):return result(False,digest)
        return result(True,digest)
