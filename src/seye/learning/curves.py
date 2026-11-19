"""Independent subset fits against fixed validation; no test-set learning curves."""
from seye.learning.packet_linear import fit
from seye.learning.packet_prototypes import records_digest


def learning_curve(training,validation,counts=(1,2,3),config=None):
    if not isinstance(counts,(list,tuple)) or not 1<=len(counts)<=5 or any(type(n) is not int or n<=0 for n in counts) or len(set(counts))!=len(counts):raise ValueError('Bounded unique sample counts required')
    labels=sorted({r['label'] for r in training});points=[]
    for count in sorted(counts):
        subset=[]
        for label in labels:
            rows=sorted([r for r in training if r['label']==label],key=lambda r:r['id'])
            if count>len(rows):raise ValueError('Curve cannot claim missing training samples')
            subset.extend(rows[:count])
        model=fit(subset,validation,**(config or {}));best=model['history'][model['best_epoch']-1]
        points.append({'per_class':count,'training_samples':len(subset),'best_epoch':model['best_epoch'],
                       'training':best['training'],'validation':best['validation'],'training_sha256':records_digest(subset)})
    return {'points':points,'validation_sha256':records_digest(validation),'test_data_used':False,
            'scope':'generated subset fits; curves do not establish learning of new representations'}
