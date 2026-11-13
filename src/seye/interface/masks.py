"""Bounded mask transformations with explicit changed-pixel accounting."""
from PIL import Image
from seye.interface.boundaries import binary


def split_projection(mask, axis='x', max_bridge=1, min_span=4):
    if axis not in ('x','y') or type(max_bridge) is not int or not 0<=max_bridge<=8 or type(min_span) is not int or min_span<2:
        raise ValueError('Invalid projection policy')
    image=binary(mask);w,h=image.size;n=w if axis=='x' else h
    if n>4096:raise ValueError('Projection axis exceeds 4096 pixels')
    counts=[image.crop((i,0,i+1,h) if axis=='x' else (0,i,w,i+1)).histogram()[255] for i in range(n)]
    spans=[];start=None
    for i,count in enumerate(counts+[0]):
        if count>max_bridge and start is None:start=i
        if count<=max_bridge and start is not None:
            if i-start>=min_span:spans.append((start,i))
            start=None
    if len(spans)>64:raise ValueError('Too many projected parts')
    if len(spans)<2:return {'parts':[{'box':[0,0,w,h],'mask':image}],'split':False,'discarded_pixels':0,'reason':'no supported projection valley'}
    parts=[]
    for left,right in spans:
        box=(left,0,right,h) if axis=='x' else (0,left,w,right)
        crop=image.crop(box);extent=crop.getbbox()
        if extent:
            actual=[box[0]+extent[0],box[1]+extent[1],box[0]+extent[2],box[1]+extent[3]]
            parts.append({'box':actual,'mask':image.crop(actual)})
    discarded=image.histogram()[255]-sum(p['mask'].histogram()[255] for p in parts)
    return {'parts':parts,'split':True,'discarded_pixels':discarded,'reason':'low-density projection valley; thin structures may be removed'}
