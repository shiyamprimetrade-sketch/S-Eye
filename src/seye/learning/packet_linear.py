"""Independently seeded SGD over schema-bound fixed features; no pretrained weights."""
import copy,math,random
from seye.core.storage import checksum
from seye.recognition.similarity import validate_packet
from seye.learning.packet_prototypes import fit as fit_prototypes,validate_model as validate_prototypes


def _scores(weights,bias,values):
    logits=[sum(w*x for w,x in zip(row,values))+b for row,b in zip(weights,bias)];peak=max(logits)
    exp=[math.exp(v-peak) for v in logits];total=sum(exp)
    return [v/total for v in exp]


def validate(model):
    if not isinstance(model,dict) or model.get('kind')!='seye-packet-linear-v1':raise ValueError('Schema-bound linear model required')
    labels=model.get('classes');dimension=model.get('dimension')
    if not isinstance(labels,list) or not 2<=len(labels)<=64 or any(not isinstance(n,str) or not n or n=='__unknown__' for n in labels) or len(set(labels))!=len(labels) or type(dimension) is not int or not 1<=dimension<=4096:raise ValueError('Invalid linear dimensions/classes')
    schema=model.get('schema');validate_packet({'schema':schema,'schema_sha256':model.get('schema_sha256'),'features':[0.0]*dimension})
    if not isinstance(model.get('weights'),list) or len(model['weights'])!=len(labels) or not isinstance(model.get('bias'),list) or len(model['bias'])!=len(labels):raise ValueError('Invalid linear parameter inventory')
    for row in model['weights']:
        if not isinstance(row,list) or len(row)!=dimension or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e6 for v in row):raise ValueError('Invalid linear weights')
    if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e6 for v in model['bias']):raise ValueError('Invalid linear biases')
    validate_prototypes(model['support_prototypes'])
    if model['support_prototypes']['schema_sha256']!=model['schema_sha256'] or model['support_prototypes']['classes']!=labels:raise ValueError('Linear support schema/class mismatch')
    return model


def scores(model,packet):
    validate(model);validate_packet(packet)
    if packet['schema_sha256']!=model['schema_sha256']:raise ValueError('Linear inference preprocessing mismatch')
    return _scores(model['weights'],model['bias'],packet['features'])


def fit(training,validation,epochs=80,seed=113,learning_rate=.2):
    support=fit_prototypes(training,validation);labels=support['classes'];dimension=training[0]['packet']['schema']['dimension']
    if type(epochs) is not int or not 1<=epochs<=300 or type(seed) is not int or type(learning_rate) not in (int,float) or not math.isfinite(learning_rate) or not 0<learning_rate<=1:raise ValueError('Invalid SGD configuration')
    if len(labels)>64 or epochs*(len(training)+len(validation))*len(labels)*dimension>30_000_000:raise ValueError('Linear training work budget exceeded')
    if any(abs(v)>1 for row in training+validation for v in row['packet']['features']):raise ValueError('Linear training requires normalized features in [-1,1]')
    rng=random.Random(seed);weights=[[rng.uniform(-.01,.01) for _ in range(dimension)] for label in labels];bias=[0.0]*len(labels)
    initial=checksum(weights);history=[];order=list(range(len(training)));best=None
    def metrics(rows):
        rows=[r for r in rows if r['label'] in labels];loss=correct=0
        for row in rows:
            probabilities=_scores(weights,bias,row['packet']['features']);target=labels.index(row['label'])
            loss-=math.log(max(1e-15,probabilities[target]));correct+=max(range(len(labels)),key=lambda i:probabilities[i])==target
        return {'cross_entropy':loss/len(rows),'correct':correct,'samples':len(rows)}
    initial_metrics=metrics(training)
    for epoch in range(1,epochs+1):
        rng.shuffle(order)
        for index in order:
            row=training[index];values=row['packet']['features'];probabilities=_scores(weights,bias,values);target=labels.index(row['label'])
            for c in range(len(labels)):
                gradient=probabilities[c]-int(c==target);bias[c]-=learning_rate*gradient
                weights[c]=[w-learning_rate*gradient*x for w,x in zip(weights[c],values)]
        entry={'epoch':epoch,'training':metrics(training),'validation':metrics(validation)};history.append(entry)
        if best is None or entry['validation']['cross_entropy']<best[0]:best=(entry['validation']['cross_entropy'],copy.deepcopy(weights),bias[:],epoch)
    model={'kind':'seye-packet-linear-v1','classes':labels,'schema':copy.deepcopy(training[0]['packet']['schema']),
           'schema_sha256':support['schema_sha256'],'dimension':dimension,'weights':best[1],'bias':best[2],
           'seed':seed,'epochs':epochs,'learning_rate':learning_rate,'initial_weights_sha256':initial,
           'initial_training':initial_metrics,'history':history,'best_epoch':best[3],'selected_by':'validation_cross_entropy_only',
           'support_prototypes':support,'training_sha256':support['training_sha256'],'validation_sha256':support['validation_sha256'],
           'pretrained_weights_used':False,'probability_calibrated':False}
    return validate(model)
