"""Common-grid or explicitly normalized geometric correspondence; no semantic identity."""
from collections import Counter
import math
from seye.scenes.spatial import frame
from seye.detection.metrics import detection_metrics,box_iou


def compare_layout(before,after,normalize=False,threshold=.5):
    frame(before);frame(after)
    if type(normalize) is not bool or type(threshold) not in (int,float) or not math.isfinite(threshold) or not 0<threshold<=1:raise ValueError('Explicit comparison policy required')
    size_a,size_b=before.get('source_size'),after.get('source_size')
    if size_a is None or size_b is None or (not normalize and list(size_a)!=list(size_b)):
        return {'comparable':False,'reason':'source_grid_unknown_or_changed','matches':[],'missing':[],'appeared':[],'geometric_similarity':None}
    def rows(value):
        w,h=value['source_size'];result=[]
        for i,r in enumerate(value['objects']):
            box=list(r['box'])
            if normalize:box=[box[0]/w,box[1]/h,box[2]/w,box[3]/h]
            result.append({'id':i,'class':r.get('class','unknown'),'box':box})
        return result
    a,b=rows(before),rows(after);metrics=detection_metrics(a,b,threshold);matched_a={r['expected'] for r in metrics['matches']};matched_b={r['predicted'] for r in metrics['matches']}
    alternatives=[{'before':i,'after_candidates':[j for j,y in enumerate(b) if x['class']==y['class'] and box_iou(x['box'],y['box'])>=threshold]} for i,x in enumerate(a)]
    reverse_counts=Counter(j for r in alternatives for j in r['after_candidates'])
    ambiguous=any(len(r['after_candidates'])>1 for r in alternatives) or any(n>1 for n in reverse_counts.values())
    counts_a,counts_b=Counter(r['class'] for r in a),Counter(r['class'] for r in b);labels=counts_a.keys()|counts_b.keys()
    union=sum(max(counts_a[k],counts_b[k]) for k in labels);intersection=sum(min(counts_a[k],counts_b[k]) for k in labels)
    return {'comparable':True,'matches':metrics['matches'],'missing':[i for i in range(len(a)) if i not in matched_a],
            'appeared':[i for i in range(len(b)) if i not in matched_b],'alternatives':alternatives,'ambiguous_correspondence':ambiguous,
            'geometric_similarity':len(metrics['matches'])/max(len(a),len(b)) if a or b else 1.0,
            'class_count_overlap':intersection/union if union else 1.0,'normalization_applied':normalize,
            'confidence_probability':None,'scope':'class/box layout agreement only; equivalent geometry is not scene or object identity'}
