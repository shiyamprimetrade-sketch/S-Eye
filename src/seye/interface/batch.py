"""Sequential bounded image observations; each item has its own error receipt."""
from seye.image.ingestion import load_image
from seye.interface.observer import observe


def observe_batch(paths,options=None):
    if not isinstance(paths,list) or not 1<=len(paths)<=32:raise ValueError('1..32 explicit image paths required')
    options={} if options is None else options
    if not isinstance(options,dict) or set(options)-{'stride','min_similarity','matcher','scales','region_proposals','region_mode'}:
        raise ValueError('Unsupported batch observation options')
    items=[];used_bytes=used_pixels=0
    for index,path in enumerate(paths):
        try:
            remaining_bytes=min(32*1024*1024,64*1024*1024-used_bytes)
            remaining_pixels=min(4_000_000,8_000_000-used_pixels)
            if min(remaining_bytes,remaining_pixels)<=0:raise ValueError('Batch read/decode budget exhausted')
            image,source=load_image(path,max_bytes=remaining_bytes,max_pixels=remaining_pixels)
            used_bytes+=source['bytes'];used_pixels+=image.width*image.height
            result=observe(path,**options,_decoded=(image,source))
            items.append({'index':index,'success':True,'observation':result})
        except (ValueError,OSError,TypeError,KeyError) as error:
            items.append({'index':index,'success':False,'error':{'type':type(error).__name__,'message':str(error)}})
    return {'schema_version':1,'items':items,'successful_items':sum(i['success'] for i in items),
            'failed_items':sum(not i['success'] for i in items),'decoded_pixels':used_pixels,'accepted_encoded_bytes':used_bytes,
            'scope':'sequential read-only observations; failed bounded reads/decodes can consume additional work; no memory writes or automatic actions'}
