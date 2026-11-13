"""Model-bound empirical correctness frequencies fitted only to declared validation."""
import math
from seye.core.storage import checksum
from seye.learning.packet_prototypes import nearest,validate_records,records_digest
from seye.learning.calibration import fit,estimate


def bind(model,validation):
    validate_records(validation)
    if records_digest(validation)!=model['validation_sha256']:raise ValueError('Calibration must use the model validation partition only')
    predictions=[nearest(model,row['packet'])[0] for row in validation]
    scores=[1/(1+p['distance']) for p in predictions];truth=[p['label']==r['label'] for p,r in zip(predictions,validation)]
    result={'model_sha256':checksum(model),'validation_sha256':records_digest(validation),'calibrator':fit(scores,truth)}
    result['calibration_sha256']=checksum(result)
    return result


def support(model,binding,packet):
    if not isinstance(binding,dict) or binding.get('calibration_sha256')!=checksum({k:v for k,v in binding.items() if k!='calibration_sha256'}):raise ValueError('Calibration integrity mismatch')
    if binding.get('model_sha256')!=checksum(model) or binding.get('validation_sha256')!=model.get('validation_sha256'):raise ValueError('Calibration model binding mismatch')
    calibration=binding.get('calibrator',{});blocks=calibration.get('blocks')
    if calibration.get('method')!='validation_isotonic_frequency' or not isinstance(blocks,list) or not blocks or len(blocks)>10000:raise ValueError('Invalid empirical calibration')
    previous=-1;count=0
    for block in blocks:
        for key in ('lower','upper'):
            if type(block.get(key)) not in (int,float) or not math.isfinite(block[key]) or not 0<=block[key]<=1:raise ValueError('Invalid calibration score range')
        if block['lower']>block['upper'] or block['lower']<=previous:raise ValueError('Calibration block order invalid')
        previous=block['upper'];n=block.get('count');total=block.get('total')
        if type(n) is not int or n<=0 or type(total) is not int or not 0<=total<=n:raise ValueError('Invalid calibration support')
        count+=n
    if count!=calibration.get('samples'):raise ValueError('Calibration sample count mismatch')
    candidate=nearest(model,packet)[0]
    return estimate(calibration,1/(1+candidate['distance']))
