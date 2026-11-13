"""Compare evidence-bearing stored scenes only on a known common source grid."""
from seye.memory.store import validate_record
from seye.scenes.relations import inventory,compare
from seye.detection.metrics import box_iou


def observed_scene(record):
    validate_record(record);analysis=record.get('analysis',{})
    if not isinstance(analysis,dict):raise ValueError('Structured observation analysis required')
    source=analysis.get('source',{});size=source.get('size') if isinstance(source,dict) else None
    if size is not None and (not isinstance(size,list) or len(size)!=2 or any(type(v) is not int or v<=0 for v in size)):raise ValueError('Valid source pixel grid required')
    regions=analysis.get('region_proposals',{}).get('regions') if isinstance(analysis.get('region_proposals',{}),dict) else None
    rows=regions if regions is not None else analysis.get('objects',[])
    scene=inventory(rows)
    if size is not None and any(not 0<=r['box'][0]<r['box'][2]<=size[0] or not 0<=r['box'][1]<r['box'][3]<=size[1] for r in scene['objects']):raise ValueError('Scene box outside source grid')
    return dict(scene,source_size=size,source_sha256=record['provenance'].get('source_sha256'),
                scope='geometric/visual region evidence, not semantic scene understanding')


def compare_observations(before,after):
    a,b=observed_scene(before),observed_scene(after)
    if a['source_size'] is None or b['source_size'] is None or a['source_size']!=b['source_size']:
        return {'comparable':False,'reason':'source_grid_missing_or_changed','matched':[],'missing':[],'appeared':[]}
    r=compare(a['objects'],b['objects']);ambiguous=any(sum(x['class']==y['class'] and box_iou(x['box'],y['box'])>=.3 for y in b['objects'])>1 for x in a['objects'])
    return dict(r,comparable=True,ambiguous_correspondence=ambiguous,
                scope='unregistered common-grid class/IoU correspondence; changes are hypotheses, not proven object histories')
