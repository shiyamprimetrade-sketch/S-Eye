"""Conservative pairing of nearby inner/outer rectangular boundary hypotheses."""
from seye.detection.metrics import box_iou,valid_box


def pair_boundaries(regions, max_gap=3):
    if not isinstance(regions,list) or len(regions)>128:raise ValueError('At most 128 regions required')
    if type(max_gap) is not int or not 1<=max_gap<=8:raise ValueError('Boundary gap must be in [1,8]')
    for r in regions:valid_box(r['box'])
    parent=list(range(len(regions)))
    def root(i):
        while parent[i]!=i:i=parent[i]
        return i
    links=[]
    for i,a in enumerate(regions):
        for j in range(i+1,len(regions)):
            b=regions[j];x,y=a['box'],b['box']
            outer,inner=(x,y) if x[0]<=y[0] and x[1]<=y[1] and x[2]>=y[2] and x[3]>=y[3] else (y,x)
            gaps=[inner[0]-outer[0],inner[1]-outer[1],outer[2]-inner[2],outer[3]-inner[3]]
            if all(0<=g<=max_gap for g in gaps) and sum(gaps)>0 and box_iou(x,y)>=.65:
                parent[root(j)]=root(i);links.append([i,j])
    groups={}
    for i in range(len(regions)):groups.setdefault(root(i),[]).append(i)
    result=[]
    for indices in groups.values():
        chosen=max(indices,key=lambda i:(regions[i]['box'][2]-regions[i]['box'][0])*(regions[i]['box'][3]-regions[i]['box'][1]))
        result.append(dict(regions[chosen],source_region_indices=indices,
                           boundary_pair_status='paired_hypothesis' if len(indices)>1 else 'unpaired'))
    result.sort(key=lambda r:(r['box'][1],r['box'][0],r['box'][3],r['box'][2]))
    return {'regions':[dict(r,id=f'region-{i+1:03d}') for i,r in enumerate(result)],'links':links,
            'input_count':len(regions),'output_count':len(result),
            'limitation':'Close nested true controls can resemble outline pairs; pairing is geometric, not semantic.'}
