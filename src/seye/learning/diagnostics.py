"""Train/validation warnings are heuristics, never proof of generalization."""
import math


def overfitting(history):
    if not isinstance(history,list) or not history:raise ValueError('Nonempty ordered history required')
    for i,row in enumerate(history,1):
        if not isinstance(row,dict) or row.get('epoch')!=i:raise ValueError('Training epochs must be contiguous')
        for split in ('training','validation'):
            metrics=row.get(split,{})
            if not isinstance(metrics,dict) or type(metrics.get('samples')) is not int or metrics['samples']<=0 or type(metrics.get('correct')) is not int or not 0<=metrics['correct']<=metrics['samples']:raise ValueError('Invalid sample/correct counts')
            loss=metrics.get('cross_entropy')
            if type(loss) not in (int,float) or not math.isfinite(loss) or loss<0:raise ValueError('Finite nonnegative cross entropy required')
    last=history[-1];train=last['training'];val=last['validation']
    gap=train['correct']/train['samples']-val['correct']/val['samples'];rise=val['cross_entropy']-min(r['validation']['cross_entropy'] for r in history)
    return {'accuracy_gap':gap,'validation_loss_rise':rise,'overfit_warning':gap>.2 or rise>.1,
            'thresholds':{'accuracy_gap':.2,'validation_loss_rise':.1},'test_data_used':False,
            'scope':'fixed heuristic warnings; no warning is not evidence of broad generalization'}
