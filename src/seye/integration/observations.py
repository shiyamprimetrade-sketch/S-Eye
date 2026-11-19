"""Single-capture source binding; pixels are evidence, never executable instructions."""
from seye.image.ingestion import load_image
from seye.memory.identity import pixel_identity
from seye.interface.observer import observe


def capture(path,expected_source_sha256=None):
    if expected_source_sha256 is not None and (not isinstance(expected_source_sha256,str) or len(expected_source_sha256)!=64 or any(c not in '0123456789abcdef' for c in expected_source_sha256)):
        raise ValueError('Expected source SHA-256 must be lowercase hexadecimal')
    image,source=load_image(path,max_pixels=4_000_000)
    if expected_source_sha256 is not None and source['sha256']!=expected_source_sha256:raise ValueError('Source digest does not match request')
    source['pixel_sha256']=pixel_identity(image)
    return image,source


def prepare_record(path,request_id,components,expected_source_sha256=None):
    from seye.recognition.pipeline import FeaturePipeline
    image,source=capture(path,expected_source_sha256)
    analysis=observe(path,_decoded=(image,source))
    packet=FeaturePipeline().extract(image,components)
    record={'schema_version':1,'features':None,'packet':packet,'analysis':analysis,
            'provenance':{'kind':'source_bound_interface_observation','source_sha256':source['sha256'],
                          'pixel_sha256':source['pixel_sha256'],'request_id':request_id}}
    return record


def persist(memory,record):
    source=record['analysis']['source'];packet=record['packet']
    identifier=memory.put(record)
    return {'observation_id':identifier,'source':source,'schema_sha256':packet['schema_sha256'],
            'semantic_identity_proven':False,'automatic_action_authorized':False}


def observe_image(path,expected_source_sha256=None,options=None):
    from seye.core.storage import checksum
    image,source=capture(path,expected_source_sha256)
    options={'region_proposals':True,'region_mode':'refined'} if options is None else options
    if not isinstance(options,dict) or set(options)-{'stride','min_similarity','matcher','scales','region_proposals','region_mode'}:raise ValueError('Unsupported image observation options')
    result=observe(path,**options,_decoded=(image,source))
    return {'schema_version':1,'observation':result,
            'identity':{'source_sha256':source['sha256'],'pixel_sha256':source['pixel_sha256'],'observation_sha256':checksum(result)},
            'semantic_identity_proven':False,'automatic_action_authorized':False,
            'scope':'the captured file bytes and decoded pixels; does not claim the external file stayed unchanged after capture'}
