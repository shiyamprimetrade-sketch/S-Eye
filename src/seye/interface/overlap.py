"""Experimental visible-color components and box-overlap ambiguity; no hidden pixels."""
from array import array
from collections import Counter
from seye.detection.metrics import box_iou


def visible_regions(image,min_area=16):
    if image.width*image.height>1_000_000 or not image.width or not image.height:raise ValueError('Visible-color mode requires 1..1000000 pixels')
    if type(min_area) is not int or not 1<=min_area<=4096:raise ValueError('Invalid visible-region area')
    image=image.convert('RGB');w,h=image.size;raw=image.tobytes()
    colors=array('H',((raw[i]//32)*64+(raw[i+1]//32)*8+raw[i+2]//32 for i in range(0,len(raw),3)))
    border=[colors[y*w+x] for y in range(h) for x in range(w) if x in (0,w-1) or y in (0,h-1)]
    background=Counter(border).most_common(1)[0][0]
    active=bytearray(value!=background for value in colors)
    if sum(active)>200_000:raise ValueError('Visible-color foreground budget exceeded')
    regions=[];components=0
    for seed in range(len(active)):
        if not active[seed]:continue
        components+=1
        if components>10_000:raise ValueError('Visible-color component budget exceeded')
        color=colors[seed];pending=[seed];active[seed]=0;points=[]
        while pending:
            index=pending.pop();points.append(index);x=index%w;y=index//w
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    nx,ny=x+dx,y+dy
                    if (dx or dy) and 0<=nx<w and 0<=ny<h:
                        nxt=ny*w+nx
                        if active[nxt] and colors[nxt]==color:active[nxt]=0;pending.append(nxt)
        if len(points)<min_area:continue
        points.sort();runs=[];start=last=points[0]
        for index in points[1:]:
            if index!=last+1 or index//w!=last//w:
                runs.append([start//w,start%w,last%w+1]);start=index
            last=index
        runs.append([start//w,start%w,last%w+1])
        box=[min(i%w for i in points),min(i//w for i in points),max(i%w for i in points)+1,max(i//w for i in points)+1]
        regions.append({'box':box,'class':'interface_region','semantic_label':None,'clickability':'unknown',
                        'color_bin':color,'visible_pixels':len(points),
                        'mask':{'encoding':'source-row-runs-v1','source_size':[w,h],'runs':runs,'scope':'visible quantized-color component only; hidden extent unknown'}})
        if len(regions)>128 or sum(len(r['mask']['runs']) for r in regions)>20_000:raise ValueError('Visible-region output budget exceeded')
    regions.sort(key=lambda r:(r['box'][1],r['box'][0],r['color_bin']))
    regions=[dict(r,id=f'visible-{i+1:03d}') for i,r in enumerate(regions)]
    overlaps=[{'first':a['id'],'second':b['id'],'box_iou':box_iou(a['box'],b['box']),'depth_order':'unknown'}
              for i,a in enumerate(regions) for b in regions[i+1:] if box_iou(a['box'],b['box'])>0]
    return {'method':'visible_quantized_color_components','regions':regions,'overlaps':overlaps,
            'candidate_count':len(regions),'complete':True,'truncated':False,'background_color_bin':background,
            'limitation':'Dominant border color is a heuristic. Same-color overlaps, hidden extent and semantic instances are unsupported.'}
