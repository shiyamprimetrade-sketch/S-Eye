"""Independent, bounded local-contrast matching at explicitly requested scales."""
import math
from PIL import Image, ImageChops, ImageStat
from seye.detection.metrics import box_iou
from seye.interface.observer import _integer, MAX_CANDIDATES


def match_contrast(screen, template, stride=4, min_similarity=.99, scales=(.75,1,1.25,1.5,2)):
    _integer(stride,1,64,'stride')
    if type(min_similarity) not in (int,float) or not math.isfinite(min_similarity) or not .9 <= min_similarity <= 1:
        raise ValueError('Contrast similarity must be in [.9,1]')
    if not isinstance(scales,(list,tuple)) or not 1<=len(scales)<=5:
        raise ValueError('One to five explicit scales required')
    if any(type(s) not in (int,float) or not math.isfinite(s) or not .5<=s<=2 for s in scales) or len(set(scales))!=len(scales):
        raise ValueError('Unique finite scales in [.5,2] required')
    if not 8<=template.width<=256 or not 8<=template.height<=256:
        raise ValueError('Template dimensions must be in [8,256]')
    gray=template.convert('L')
    if ImageStat.Stat(gray).stddev[0]<8:raise ValueError('Template lacks visual contrast')
    # Local midrange threshold preserves relative structure across polarity/theme.
    low,high=gray.getextrema();binary=gray.point(lambda p:255 if p>(low+high)/2 else 0)
    plans=[];budget=0
    for scale in scales:
        width,height=round(template.width*scale),round(template.height*scale)
        if min(width,height)<8 or max(width,height)>256:raise ValueError('Scaled template dimensions outside [8,256]')
        if width>screen.width or height>screen.height:continue
        xs=range(0,screen.width-width+1,stride);ys=range(0,screen.height-height+1,stride)
        budget+=len(xs)*len(ys)
        plans.append((scale,width,height,xs,ys))
    if budget>MAX_CANDIDATES:raise ValueError('Combined scale search exceeds candidate budget; crop screenshot or increase stride')
    source=screen.convert('L');matches=[]
    for scale,width,height,xs,ys in plans:
        target=binary.resize((width,height),Image.Resampling.NEAREST)
        offsets=[(round(x*(width-1)/7),round(y*(height-1)/7)) for y in range(8) for x in range(8)]
        expected=[target.getpixel(p)>0 for p in offsets]
        for y in ys:
            for x in xs:
                patch=source.crop((x,y,x+width,y+height));lo,hi=patch.getextrema()
                if hi-lo<16:continue
                midpoint=(lo+hi)/2
                values=[patch.getpixel(p)>midpoint for p in offsets]
                wrong=sum(a!=b for a,b in zip(values,expected))
                # Sampling is a conservative screening heuristic, not a completeness proof.
                if min(wrong,64-wrong)>max(1,math.ceil((1-min_similarity)*64)):continue
                candidate=patch.point(lambda p:255 if p>midpoint else 0)
                difference=ImageStat.Stat(ImageChops.difference(candidate,target)).mean[0]/255
                similarity=1-min(difference,1-difference)
                if similarity>=min_similarity:
                    matches.append({'box':[x,y,x+width,y+height],'similarity':similarity,'scale':scale})
    matches.sort(key=lambda m:(-m['similarity'],m['box'][1],m['box'][0],m['scale']))
    distinct=[]
    for match in matches:
        if all(box_iou(match['box'],other['box'])<.3 for other in distinct):distinct.append(match)
        if len(distinct)==2:break
    ambiguous=len(distinct)>1 and distinct[0]['similarity']-distinct[1]['similarity']<=.01
    return {'status':'ambiguous' if ambiguous else 'visual_candidate' if distinct else 'not_found',
            'candidate':distinct[0] if distinct and not ambiguous else None,
            'candidates_examined':budget,'distinct_matches':len(distinct),
            'score_kind':'uncalibrated local binary contrast agreement; polarity invariant',
            'scales':list(scales),'matcher':'contrast'}
