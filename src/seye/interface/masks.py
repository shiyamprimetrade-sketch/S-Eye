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


def remove_specks(mask,min_area=4):
    if type(min_area) is not int or not 1<=min_area<=4096:raise ValueError('Invalid component area policy')
    image=binary(mask);raw=image.tobytes();active=bytearray(raw);output=bytearray(raw);w,h=image.size
    if image.histogram()[255]>200_000:raise ValueError('Noise foreground budget exceeded')
    removed=components=0
    for seed in range(len(active)):
        if not active[seed]:continue
        components+=1
        if components>10_000:raise ValueError('Noise component budget exceeded')
        pending=[seed];active[seed]=0;group=[]
        while pending:
            index=pending.pop();group.append(index);x=index%w;y=index//w
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    nx,ny=x+dx,y+dy
                    if (dx or dy) and 0<=nx<w and 0<=ny<h:
                        next_index=ny*w+nx
                        if active[next_index]:active[next_index]=0;pending.append(next_index)
        if len(group)<min_area:
            removed+=len(group)
            for index in group:output[index]=0
    return {'mask':Image.frombytes('L',image.size,bytes(output)),'removed_pixels':removed,'components':components,
            'policy':'8-connected area filtering; small real glyphs can be removed'}
