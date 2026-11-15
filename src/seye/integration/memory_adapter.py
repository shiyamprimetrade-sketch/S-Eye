"""Typed S-Memory-facing calls; each operation retains the Client's grants."""
from seye.api.client import Client


class MemoryAdapter:
    def __init__(self,client,path,writable=False):
        if not isinstance(client,Client) or not isinstance(path,str) or not path or type(writable) is not bool:raise ValueError('Client, memory path and explicit write flag required')
        self.client,self.path,self.writable=client,path,writable

    def store_image(self,image,request_id,components=None,expected_source_sha256=None):
        if not self.writable:raise PermissionError('This memory adapter is read-only')
        return self.client.call('memory_store_image',request_id,memory=self.path,image=str(image),
                                components=['shape'] if components is None else components,expected_source_sha256=expected_source_sha256)

    def observation(self,observation_id,request_id):
        return self.client.call('memory_get_observation',request_id,memory=self.path,observation_id=observation_id)

    def query_image(self,image,request_id,components=None,limit=5):
        return self.client.call('memory_packet_query',request_id,memory=self.path,image=str(image),components=['shape'] if components is None else components,limit=limit)

    def build_index(self,request_id):
        if not self.writable:raise PermissionError('This memory adapter is read-only')
        return self.client.call('memory_index_build',request_id,memory=self.path)

    def find(self,image,request_id,maximum_distance,components=None,include_self=False):
        return self.client.call('memory_find',request_id,memory=self.path,image=str(image),maximum_distance=maximum_distance,
                                components=['shape'] if components is None else components,include_self=include_self)
