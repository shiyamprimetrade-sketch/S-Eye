"""Stored scene inventories with explicit unknown semantics and local-only IDs."""
from seye.memory.scenes import observed_scene
from seye.scenes.relations import group_objects
from seye.detection.metrics import box_iou


def inventory(record):
    scene=observed_scene(record);objects=[dict(row,semantic_label=None,clickability='unknown',identity_scope='frame_local_visual_hypothesis') for row in scene['objects']]
    relations=[]
    for relation in scene['relations']:
        a,b=objects[relation['first']]['box'],objects[relation['second']]['box']
        contains_a=a[0]<=b[0] and a[1]<=b[1] and a[2]>=b[2] and a[3]>=b[3]
        contains_b=b[0]<=a[0] and b[1]<=a[1] and b[2]>=a[2] and b[3]>=a[3]
        relations.append(dict(relation,box_iou=box_iou(a,b),containment='same_bounds' if contains_a and contains_b else 'first_contains_second' if contains_a else 'second_contains_first' if contains_b else 'neither'))
    groups=group_objects(objects)['groups']
    return {'schema_version':1,'objects':objects,'relations':relations,'proximity_groups':groups,
            'visual_hypothesis_count':len(objects),'semantic_object_count':None,'source_size':scene['source_size'],
            'source_sha256':scene['source_sha256'],'confidence_probability':None,
            'scope':'stored geometric evidence only; frame IDs, groups and containment are not semantic object identities or actions'}
