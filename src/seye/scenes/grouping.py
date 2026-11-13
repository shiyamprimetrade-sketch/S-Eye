"""Alignment/proximity grouping with explicit pair evidence; no toolbar semantics."""
import math
from seye.scenes.spatial import frame,relationships


def aligned_groups(value,axis='row',maximum_gap=24,alignment_fraction=.02):
    frame(value)
    if axis not in ('row','column') or type(maximum_gap) not in (int,float) or not math.isfinite(maximum_gap) or not 0<=maximum_gap<=1000 or type(alignment_fraction) not in (int,float) or not math.isfinite(alignment_fraction) or not 0<=alignment_fraction<=.25:raise ValueError('Invalid grouping policy')
    size=value.get('source_size')
    if size is None:return {'groups':[],'links':[],'complete':False,'reason':'source_grid_unknown'}
    rows=value['objects'];parent=list(range(len(rows)));links=[];tolerance=size[1 if axis=='row' else 0]*alignment_fraction
    def root(i):
        while parent[i]!=i:i=parent[i]
        return i
    for pair in relationships(value)['relations']:
        if pair['topology'] in ('same_bounds','first_contains_second','second_contains_first'):continue
        i,j=pair['first'],pair['second'];a,b=rows[i]['box'],rows[j]['box'];coordinate=1 if axis=='row' else 0
        center_error=abs((a[coordinate]+a[coordinate+2]-b[coordinate]-b[coordinate+2])/2)
        gap=pair['edge_gap_pixels'][0 if axis=='row' else 1]
        if center_error<=tolerance and gap<=maximum_gap:
            parent[root(j)]=root(i);links.append({'first':i,'second':j,'center_error':center_error,'edge_gap':gap})
    groups={}
    for i in range(len(rows)):groups.setdefault(root(i),[]).append(i)
    return {'groups':list(groups.values()),'links':links,'complete':True,'axis':axis,'alignment_tolerance_pixels':tolerance,
            'scope':'connected alignment/proximity hypotheses; transitive groups are not semantic UI components'}
