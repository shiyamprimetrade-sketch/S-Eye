"""Consecutive non-observation evidence; never proof of semantic disappearance."""
from seye.scenes.spatial import frame
from seye.scenes.comparison import compare_layout


def _coverage(a,b):
    intersection=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    return intersection/((a[2]-a[0])*(a[3]-a[1]))


def missing_evidence(reference,observations,minimum_consecutive=2):
    frame(reference)
    if not isinstance(observations,list) or not 1<=len(observations)<=30 or type(minimum_consecutive) is not int or not 2<=minimum_consecutive<=30:raise ValueError('Bounded sequence and at least two confirmations required')
    counters=[0]*len(reference['objects']);starts=[None]*len(counters);active=[None]*len(counters);events=[];frames=[]
    for index,current in enumerate(observations):
        frame(current);comparison=compare_layout(reference,current);states=[]
        for i,obj in enumerate(reference['objects']):
            if not comparison['comparable']:state='incomparable'
            elif comparison['alternatives'][i]['after_candidates']:state='possibly_observed'
            elif any(_coverage(obj['box'],other['box'])>=.8 for other in current['objects']):state='covered_or_relabelled_unknown'
            else:state='not_observed'
            if state=='not_observed':
                counters[i]+=1
                if counters[i]==1:starts[i]=index
                if counters[i]==minimum_consecutive:
                    active[i]=len(events);events.append({'reference_region':i,'first_missing_frame':starts[i],'last_missing_frame':index,'consecutive_missing':counters[i],'assertion':'not_observed','semantic_removal_proven':False})
                elif counters[i]>minimum_consecutive:
                    events[active[i]].update(last_missing_frame=index,consecutive_missing=counters[i])
            else:counters[i]=0;starts[i]=None;active[i]=None
            states.append({'reference_region':i,'state':state,'consecutive_missing':counters[i]})
        frames.append({'index':index,'comparable':comparison['comparable'],'regions':states})
    return {'events':events,'frames':frames,'minimum_consecutive':minimum_consecutive,
            'scope':'reference-grid geometric non-observation; motion, occlusion, failed detection and application transitions remain alternative explanations'}
