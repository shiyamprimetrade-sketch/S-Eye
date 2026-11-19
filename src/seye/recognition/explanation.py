"""Evidence-grounded descriptor explanations, without invented object semantics."""
from seye.core.storage import checksum
from seye.recognition.packet_decision import candidates
from seye.recognition.similarity import compare


def explain(model,packet,top_k=3,min_margin=.005,calibration=None):
    output=candidates(model,packet,top_k,min_margin);nearest=output['candidates'][0]['label'];prototype=model['prototypes'][nearest]
    evidence=compare(packet,prototype)
    differences=sorted([{'index':i,'observed':value,'prototype':expected,'absolute_difference':abs(value-expected)}
                        for i,(value,expected) in enumerate(zip(packet['features'],prototype['features']))],key=lambda r:(-r['absolute_difference'],r['index']))[:5]
    output.update(model_sha256=checksum(model),feature_schema_sha256=packet['schema_sha256'],
                  explanation={'decision_reason':output['selection']['reason'],'nearest_training_label':nearest,
                               'component_evidence':evidence['components'],'largest_descriptor_differences':differences,
                               'scope':'descriptor comparisons against supplied training labels, not semantic visual reasoning'})
    if calibration is not None:
        from seye.learning.packet_calibration import support
        output['empirical_validation_support']=support(model,calibration,packet)
    return output
