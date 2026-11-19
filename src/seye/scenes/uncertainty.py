"""Machine-readable limits bound to exact scene evidence; no invented confidence."""
from seye.scenes.spatial import frame
from seye.core.storage import checksum


def assess(value,comparison=None):
    frame(value);complete=value.get('complete')
    if complete is not None and type(complete) is not bool:raise ValueError('Completeness must be boolean or unknown')
    source=value.get('source_sha256');valid_source=isinstance(source,str) and len(source)==64 and all(c in '0123456789abcdef' for c in source)
    flags=['semantic_identity_unknown','clickability_unknown','registration_not_inferred']
    if not valid_source:flags.append('source_identity_unavailable_or_unverified')
    if complete is False:flags.append('proposal_inventory_truncated')
    elif complete is None:flags.append('inventory_completeness_not_reported')
    state='usable_geometry' if complete is True else 'partial_geometry'
    if comparison is not None:
        if not isinstance(comparison,dict) or type(comparison.get('comparable')) is not bool:raise ValueError('Explicit comparison status required')
        if not comparison['comparable']:flags.append('comparison_incomparable');state='incomparable'
        if comparison.get('ambiguous_correspondence'):flags.append('correspondence_ambiguous')
        if comparison.get('normalization_applied'):flags.append('normalization_not_registration')
    return {'state':state,'flags':flags,'evidence_sha256':checksum(value),'comparison_sha256':checksum(comparison) if comparison is not None else None,
            'confidence_probability':None,'source_identity_available':valid_source,'inventory_complete_assertion':complete,
            'automatic_action_authorized':False,'scope':'structured geometric uncertainty; probability and action authority are not inferred'}
