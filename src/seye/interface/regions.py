"""Independent RGB neighbor edges and connected rectangular-region hypotheses.

These are unlabeled visual regions, never inferred controls or click targets.
"""
from PIL import ImageChops

MAX_PIXELS = 4_000_000
MAX_EDGE_PIXELS = 200_000
MAX_COMPONENTS = 10_000


def _integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in [{low},{high}]')


def edge_mask(image, threshold=24):
    _integer(threshold,1,255,'edge_threshold')
    if image.width*image.height>MAX_PIXELS:raise ValueError('Region image exceeds pixel budget')
    image=image.convert('RGB');width,height=image.size
    if not width or not height:raise ValueError('Nonempty region image required')
    horizontal=image.copy();vertical=image.copy()
    if width>1:horizontal.paste(image.crop((0,0,width-1,height)),(1,0))
    if height>1:vertical.paste(image.crop((0,0,width,height-1)),(0,1))
    difference=ImageChops.lighter(ImageChops.difference(image,horizontal),ImageChops.difference(image,vertical))
    red,green,blue=difference.split()
    return ImageChops.lighter(ImageChops.lighter(red,green),blue).point(lambda value:255 if value>=threshold else 0)


def propose_regions(image, edge_threshold=24, min_width=12, min_height=8, max_regions=128):
    _integer(min_width,2,4096,'min_width');_integer(min_height,2,4096,'min_height')
    _integer(max_regions,1,128,'max_regions')
    mask=edge_mask(image,edge_threshold);width,height=mask.size
    edge_count=mask.histogram()[255]
    if edge_count>MAX_EDGE_PIXELS:raise ValueError('Region edge-pixel budget exceeded')
    # Fixed scan order and bytearray make topology and IDs deterministic.
    active=bytearray(1 if p else 0 for p in mask.tobytes())
    proposals=[];components=0
    for seed in range(len(active)):
        if not active[seed]:continue
        components+=1
        if components>MAX_COMPONENTS:raise ValueError('Region component budget exceeded')
        active[seed]=0;pending=[seed];points=[]
        while pending:
            index=pending.pop();x=index%width;y=index//width;points.append((x,y))
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    nx,ny=x+dx,y+dy
                    if (dx or dy) and 0<=nx<width and 0<=ny<height:
                        neighbor=ny*width+nx
                        if active[neighbor]:active[neighbor]=0;pending.append(neighbor)
        left=min(x for x,y in points);right=max(x for x,y in points)+1
        top=min(y for x,y in points);bottom=max(y for x,y in points)+1
        w,h=right-left,bottom-top
        if w<min_width or h<min_height:continue
        # Rectangular support means observed perimeter occupancy, not control confidence.
        border=sum(x in (left,right-1) or y in (top,bottom-1) for x,y in points)
        coverage=border/(2*w+2*h-4)
        if coverage<.75:continue
        proposals.append({'box':[left,top,right,bottom],'class':'interface_region',
                          'edge_pixels':len(points),'border_coverage':coverage,
                          'semantic_label':None,'clickability':'unknown'})
    proposals.sort(key=lambda r:(r['box'][1],r['box'][0],r['box'][3],r['box'][2]))
    total=len(proposals);truncated=total>max_regions
    regions=[dict(row,id=f'region-{i+1:03d}') for i,row in enumerate(proposals[:max_regions])]
    return {'schema_version':1,'method':'rgb_neighbor_edges_8_connected_rectangular_support',
            'regions':regions,'edge_pixels':edge_count,'components':components,'candidate_count':total,
            'truncated':truncated,'complete':not truncated,
            'parameters':{'edge_threshold':edge_threshold,'min_width':min_width,'min_height':min_height,
                          'max_regions':max_regions,'min_border_coverage':.75},
            'coordinates':'EXIF-oriented source pixels; right/bottom exclusive',
            'limitations':['Unlabeled region hypotheses; not semantic controls or actionable click targets.',
                           'Overlapping/touching boundaries can merge; nested icons/text can create extra proposals.',
                           'Low contrast, gradients, clipped boundaries and nonrectangular controls may be missed.']}
