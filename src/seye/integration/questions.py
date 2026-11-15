"""Finite geometric questions with source-linked evidence and explicit abstention."""
from seye.core.storage import checksum
from seye.integration.observations import capture,observe_image
from seye.interface.observer import change_regions

SUPPORTED=('count_proposed_regions','list_region_boxes','changed_pixel_fraction')


def ask(path,question,previous=None,expected_source_sha256=None):
    if not isinstance(question,str) or not 1<=len(question)<=256:raise ValueError('Bounded question string required')
    base={'question':question,'semantic_understanding':False,'automatic_action_authorized':False}
    if question not in SUPPORTED:
        return dict(base,status='unsupported',answer=None,evidence=[],reason='No OCR, semantic button identity or action decision is supported by this geometric API')
    if question=='changed_pixel_fraction':
        if previous is None:raise ValueError('Changed-pixel question requires an explicit previous image')
        current,source=capture(path,expected_source_sha256);prior,prior_source=capture(previous)
        change=change_regions(prior,current)
        evidence=[{'source':source,'previous_source':prior_source,'change_report_sha256':checksum(change)}]
        return dict(base,status='answered' if change['comparable'] else 'incomparable',answer=change['changed_fraction'],evidence=evidence,
                    scope='thresholded pixel difference on the same grid, not proof of semantic scene change')
    observed=observe_image(path,expected_source_sha256)
    regions=observed['observation']['region_proposals']['regions']
    boxes=[list(row['box']) for row in regions]
    answer=len(boxes) if question=='count_proposed_regions' else boxes
    return dict(base,status='answered',answer=answer,
                evidence=[{'source':observed['observation']['source'],'observation_sha256':observed['identity']['observation_sha256'],
                           'region_indices':list(range(len(boxes)))}],
                scope='unlabeled geometric region hypotheses; not semantic objects or clickable controls')
