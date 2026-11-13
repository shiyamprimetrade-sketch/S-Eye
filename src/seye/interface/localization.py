"""Source-coordinate region boxes and actual observed edge masks, never filled boxes."""
import hashlib
from PIL import Image
from seye.interface.regions import edge_mask,propose_regions
from seye.interface.grouping import pair_boundaries


def decode_runs(size,runs):
    if not isinstance(size,(list,tuple)) or len(size)!=2 or any(type(v) is not int or v<=0 for v in size) or size[0]*size[1]>4_000_000:
        raise ValueError('Invalid source mask size')
    if not isinstance(runs,list) or len(runs)>20_000:raise ValueError('Invalid run budget')
    w,h=size;image=Image.new('L',size);last=None
    for run in runs:
        if not isinstance(run,list) or len(run)!=3 or any(type(v) is not int for v in run):raise ValueError('Invalid run')
        y,left,right=run
        if not 0<=y<h or not 0<=left<right<=w or (last is not None and (y<last[0] or (y==last[0] and left<last[2]))):raise ValueError('Runs must be ordered, nonoverlapping and inside source')
        image.paste(255,(left,y,right,y+1));last=run
    return image


def localize(image):
    raw=propose_regions(image);paired=pair_boundaries(raw['regions']);mask=edge_mask(image);pixels=mask.load()
    w,h=image.size;regions=[];area=run_count=0
    for region in paired['regions']:
        left,top,right,bottom=region['box'];area+=(right-left)*(bottom-top)
        if area>8_000_000:raise ValueError('Combined region mask workspace exceeded')
        runs=[]
        for y in range(top,bottom):
            start=None
            for x in range(left,right+1):
                on=x<right and pixels[x,y]>0
                if on and start is None:start=x
                if not on and start is not None:
                    runs.append([y,start,x]);start=None;run_count+=1
                    if run_count>20_000:raise ValueError('Combined region mask run budget exceeded')
        regions.append(dict(region,mask={'encoding':'source-row-runs-v1','source_size':[w,h],'runs':runs,
                                        'scope':'all observed edge pixels inside region; not instance foreground'}))
    return dict(raw,method='paired_rectangular_boundaries_with_observed_edge_masks',regions=regions,
                raw_candidate_count=raw['candidate_count'],candidate_count=len(regions),pair_links=paired['links'],
                edge_mask_sha256=hashlib.sha256(f'L:{w}:{h}:'.encode()+mask.tobytes()).hexdigest(),
                mask_scope='source-grid edge strokes; overlap/nesting can share pixels')
