"""Projective normalization from caller-supplied corners, not inferred perspective."""
import math
from PIL import Image


def _solve(matrix,values):
    rows=[list(row)+[value] for row,value in zip(matrix,values)];n=len(values)
    for column in range(n):
        pivot=max(range(column,n),key=lambda i:abs(rows[i][column]))
        if abs(rows[pivot][column])<1e-10:raise ValueError('Singular projective geometry')
        rows[column],rows[pivot]=rows[pivot],rows[column]
        scale=rows[column][column];rows[column]=[v/scale for v in rows[column]]
        for i in range(n):
            if i==column:continue
            scale=rows[i][column];rows[i]=[a-scale*b for a,b in zip(rows[i],rows[column])]
    result=[row[-1] for row in rows]
    if not all(math.isfinite(x) for x in result):raise ValueError('Nonfinite projective solution')
    return result


def rectify(image,quad,size=(64,64)):
    if not isinstance(size,(list,tuple)) or len(size)!=2 or any(type(v) is not int or not 2<=v<=1024 for v in size):raise ValueError('Canonical dimensions must be in [2,1024]')
    if image.width*image.height>4_000_000:raise ValueError('Source exceeds perspective pixel budget')
    if not isinstance(quad,(list,tuple)) or len(quad)!=4:raise ValueError('Four ordered source corners required')
    for point in quad:
        if not isinstance(point,(list,tuple)) or len(point)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in point):raise ValueError('Finite corner coordinates required')
        if not 0<=point[0]<image.width or not 0<=point[1]<image.height:raise ValueError('Corner outside source')
    crosses=[]
    for i in range(4):
        a,b,c=quad[i],quad[(i+1)%4],quad[(i+2)%4]
        crosses.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
    if not (all(c>1e-8 for c in crosses) or all(c< -1e-8 for c in crosses)):raise ValueError('Ordered convex nondegenerate quad required')
    w,h=size;canonical=[(0,0),(w-1,0),(w-1,h-1),(0,h-1)];matrix=[];values=[]
    for (u,v),(x,y) in zip(canonical,quad):
        matrix += [[u,v,1,0,0,0,-x*u,-x*v],[0,0,0,u,v,1,-y*u,-y*v]];values += [x,y]
    coefficients=_solve(matrix,values)
    errors=[]
    for (u,v),(x,y) in zip(canonical,quad):
        a,b,c,d,e,f,g,k=coefficients;den=g*u+k*v+1
        if den<=1e-10:raise ValueError('Projective horizon in output domain')
        errors.append(math.hypot((a*u+b*v+c)/den-x,(d*u+e*v+f)/den-y))
    output=image.convert('RGB').transform(tuple(size),Image.Transform.PERSPECTIVE,coefficients,Image.Resampling.BILINEAR)
    return output,{'method':'caller_corner_projective_normalization','source_quad':[list(p) for p in quad],
                   'canonical_size':list(size),'output_to_source_coefficients':coefficients,
                   'max_corner_reprojection_error':max(errors),'corner_origin':'caller_supplied',
                   'limitation':'No automatic corner detection or physical viewpoint invariance validation.'}
