"""Versioned, explicitly registered feature components; no runtime imports from requests."""
import math
import re
from PIL import Image,ImageStat
from seye.core.storage import checksum
from seye.recognition.features import extract,FEATURE_VERSION
from seye.interface.regions import edge_mask,propose_regions


def interface_features(image):
    image=image.convert('RGB');image.thumbnail((128,128))
    edges=edge_mask(image);means=ImageStat.Stat(image).mean;gray=ImageStat.Stat(image.convert('L'))
    occupancy=[v/255 for v in edges.resize((4,4),Image.Resampling.BOX).get_flattened_data()]
    regions=propose_regions(image)['regions'];area=image.width*image.height
    largest=max(((r['box'][2]-r['box'][0])*(r['box'][3]-r['box'][1])/area for r in regions),default=0)
    return occupancy+[v/255 for v in means]+[gray.stddev[0]/255,edges.histogram()[255]/area,len(regions)/128,largest]


class FeaturePipeline:
    def __init__(self):
        self._components={}
        self.register('legacy',FEATURE_VERSION,91,extract)
        self.register('interface','interface-structure-v1',23,interface_features)
        from seye.recognition.descriptors import geometry,appearance,shape
        self.register('geometry','geometry-v1',12,geometry)
        self.register('appearance','appearance-v1',30,appearance)
        self.register('shape','edge-centered-shape-v1',257,shape)

    def register(self,name,version,dimension,function):
        if not isinstance(name,str) or not re.fullmatch('[a-z][a-z0-9_.-]{0,63}',name) or name in self._components:
            raise ValueError('Unique feature name required')
        if not isinstance(version,str) or not 1<=len(version)<=64 or type(dimension) is not int or not 1<=dimension<=4096 or not callable(function):
            raise ValueError('Version, bounded dimension and callable extractor required')
        self._components[name]=(version,dimension,function)

    def _selection(self,components):
        if not isinstance(components,(list,tuple)) or not 1<=len(components)<=8 or any(not isinstance(n,str) for n in components) or len(set(components))!=len(components):
            raise ValueError('Unique explicit feature selection required')
        if any(n not in self._components for n in components):raise ValueError('Unknown feature component')
        if sum(self._components[n][1] for n in components)>4096:raise ValueError('Combined feature budget exceeded')
        return list(components)

    def schema(self,components=('interface',)):
        selected=self._selection(components);parts=[];offset=0
        for name in selected:
            version,dimension,_=self._components[name]
            parts.append({'name':name,'version':version,'dimension':dimension,'offset':offset});offset+=dimension
        contract={'version':'seye-feature-pipeline-v1','components':parts,'dimension':offset}
        return {'schema':contract,'schema_sha256':checksum(contract)}

    def extract(self,image,components=('interface',)):
        components=self._selection(components)
        vector=[];schema=[]
        for name in components:
            version,dimension,function=self._components[name];values=function(image.copy())
            if not isinstance(values,list) or len(values)!=dimension or any(type(v) not in (int,float) or not math.isfinite(v) for v in values):raise ValueError('Extractor violated finite dimension contract')
            schema.append({'name':name,'version':version,'dimension':dimension,'offset':len(vector)})
            vector.extend(float(v) for v in values)
        contract={'version':'seye-feature-pipeline-v1','components':schema,'dimension':len(vector)}
        return {'features':vector,'schema':contract,'schema_sha256':checksum(contract),
                'scope':'independent descriptors, not learned recognition or calibrated confidence'}

    def extract_many(self,image,selections):
        """Reuse each selected component once for one immutable input image.

        Built-ins are deterministic. Custom registered functions must be pure for
        equivalence with repeated independent extraction to hold.
        """
        if not isinstance(selections,(list,tuple)) or not 1<=len(selections)<=32:
            raise ValueError('1..32 feature selections required')
        selected=[self._selection(names) for names in selections]
        if sum(self._components[name][1] for names in selected for name in names)>32768:
            raise ValueError('Combined packet output budget exceeded')
        names=list(dict.fromkeys(name for group in selected for name in group))
        singles={name:self.extract(image,[name]) for name in names}
        packets=[]
        for group in selected:
            features=[];schema=[]
            for name in group:
                packet=singles[name];part=dict(packet['schema']['components'][0],offset=len(features))
                schema.append(part);features.extend(packet['features'])
            contract={'version':'seye-feature-pipeline-v1','components':schema,'dimension':len(features)}
            packets.append({'features':features,'schema':contract,'schema_sha256':checksum(contract),
                            'scope':'independent descriptors, not learned recognition or calibrated confidence'})
        requested=sum(map(len,selected))
        return {'packets':packets,'component_extractions':len(names),'reused_component_requests':requested-len(names),
                'scope':'within one image only; no source read/decode cache or learned inference speed claim'}
