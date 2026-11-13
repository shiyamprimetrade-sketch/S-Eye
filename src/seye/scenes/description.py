"""Deterministic descriptions whose assertions reference actual geometric evidence."""
from seye.scenes.spatial import relationships


def describe(value,maximum_facts=12):
    if type(maximum_facts) is not int or not 1<=maximum_facts<=20:raise ValueError('Description fact limit must be in [1,20]')
    evidence=relationships(value);count=evidence['objects'];facts=[{'text':f'{count} visual hypotheses are provided.','evidence_ref':'/objects'}]
    for index,relation in enumerate(evidence['relations']):
        if len(facts)>=maximum_facts:break
        i,j=relation['first'],relation['second'];kind=relation['topology']
        facts.append({'text':f'Regions {i} and {j} have geometric relation {kind}.','evidence_ref':f'/relations/{index}'})
    return {'text':' '.join(f['text'] for f in facts),'facts':facts,'evidence':evidence,
            'complete':len(evidence['relations'])+1<=maximum_facts,'semantic_description':None,'confidence_probability':None,
            'scope':'bounded geometric statements only; no arbitrary label text, OCR, object naming or action instruction'}
