"""Explicit-lifetime packet LRU. Every lookup still reads, hashes and decodes."""
from collections import OrderedDict
import json,sys
from seye.core.storage import canonical
from seye.image.ingestion import load_image
from seye.recognition.pipeline import FeaturePipeline


class PacketCache:
    def __init__(self,max_entries=64,max_bytes=2*1024*1024):
        if type(max_entries) is not int or not 1<=max_entries<=1024 or type(max_bytes) is not int or not 1<=max_bytes<=16*1024*1024:
            raise ValueError('Bounded packet cache limits required')
        self.max_entries,self.max_bytes=max_entries,max_bytes
        self._pipeline=FeaturePipeline();self.clear()

    def clear(self):
        self._rows=OrderedDict();self._bytes=0;self.hits=self.misses=self.evictions=0

    def from_file(self,path,components=('shape',),allowed_root=None):
        image,source=load_image(path,allowed_root=allowed_root,max_pixels=4_000_000)
        identity=self._pipeline.schema(components)
        key=(source['sha256'],identity['schema_sha256'])
        if key in self._rows:
            self.hits+=1;self._rows.move_to_end(key)
            return json.loads(self._rows[key][0]),source
        self.misses+=1;packet=self._pipeline.extract(image,components);encoded=canonical(packet)
        charge=sys.getsizeof(encoded)+sys.getsizeof(key)+sum(sys.getsizeof(v) for v in key)
        if charge<=self.max_bytes:
            while self._rows and (len(self._rows)>=self.max_entries or self._bytes+charge>self.max_bytes):
                _,(_,removed)=self._rows.popitem(last=False);self._bytes-=removed;self.evictions+=1
            self._rows[key]=(encoded,charge);self._bytes+=charge
        return packet,source

    def statistics(self):
        return {'entries':len(self._rows),'tracked_entry_bytes':self._bytes,'hits':self.hits,'misses':self.misses,'evictions':self.evictions,
                'scope':'retained key/serialized-packet estimate; excludes LRU container, transient decode allocations and process RSS; fresh decode on every lookup'}
