"""Structural annotation/provenance checks, not authentication of label truth."""
from seye.learning.packet_prototypes import validate_records
from seye.detection.metrics import valid_box


def validate_annotations(records):
    validate_records(records)
    for row in records:
        if row.get('annotation_origin') not in ('renderer','human','imported_unverified'):raise ValueError('Explicit annotation provenance required')
        if row.get('source_kind') not in ('generated','screenshot','photograph','numeric_fixture'):raise ValueError('Explicit source kind required')
        if 'box' in row:
            valid_box(row['box']);size=row.get('source_size')
            if not isinstance(size,list) or len(size)!=2 or any(type(v) is not int or v<=0 for v in size) or not 0<=row['box'][0]<row['box'][2]<=size[0] or not 0<=row['box'][1]<row['box'][3]<=size[1]:raise ValueError('Annotation box outside source grid')
    return {'records':len(records),'labels':sorted({r['label'] for r in records}),'label_truth_authenticated':False}
