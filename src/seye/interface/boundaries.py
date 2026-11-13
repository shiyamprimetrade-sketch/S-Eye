"""Ordered pixel-cell boundaries, including concavities and holes; no hull replacement."""
from collections import defaultdict
from PIL import Image


def binary(mask):
    if not isinstance(mask,Image.Image) or not 0<mask.width*mask.height<=4_000_000:
        raise ValueError('Nonempty mask up to four million pixels required')
    return mask.convert('L').point(lambda v:255 if v else 0)


def contours(mask, max_edges=200_000):
    if type(max_edges) is not int or not 4<=max_edges<=200_000:raise ValueError('Invalid contour edge budget')
    mask=binary(mask);w,h=mask.size;p=mask.load();edges=set()
    for y in range(h):
        for x in range(w):
            if not p[x,y]:continue
            for neighbor,a,b in [((x,y-1),(x,y),(x+1,y)),((x+1,y),(x+1,y),(x+1,y+1)),
                                  ((x,y+1),(x+1,y+1),(x,y+1)),((x-1,y),(x,y+1),(x,y))]:
                nx,ny=neighbor
                if not (0<=nx<w and 0<=ny<h) or not p[nx,ny]:edges.add((a,b))
            if len(edges)>max_edges:raise ValueError('Contour edge budget exceeded')
    outgoing=defaultdict(set)
    for a,b in edges:outgoing[a].add(b)
    directions={(1,0):0,(0,1):1,(-1,0):2,(0,-1):3};loops=[]
    for seed in sorted(edges):
        if seed not in edges:continue
        a,b=seed;start=a;points=[a];current=(a,b)
        while True:
            a,b=current;edges.remove(current);outgoing[a].remove(b);points.append(b)
            if b==start:break
            direction=directions[(b[0]-a[0],b[1]-a[1])]
            def priority(c):
                turn=(directions[(c[0]-b[0],c[1]-b[1])]-direction)%4
                return ({1:0,0:1,3:2,2:3}[turn],c)
            choices=outgoing[b]
            if not choices:raise ValueError('Open contour topology')
            current=(b,min(choices,key=priority))
        area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]))/2
        loops.append({'points':[list(p) for p in points],'signed_area':area,'role':'outer' if area>0 else 'hole',
                      'perimeter':len(points)-1,'box':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]})
    return {'loops':loops,'foreground_pixels':mask.histogram()[255],
            'net_area':sum(loop['signed_area'] for loop in loops),'coordinates':'pixel-cell corners, not pixel centers'}
