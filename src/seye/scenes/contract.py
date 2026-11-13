"""Stable conversion from stored observation evidence, without altering old APIs."""
from seye.memory.scenes import observed_scene
from seye.memory.identity import identify
from seye.scenes.spatial import frame


def from_record(record):
    scene=observed_scene(record);identity=identify(record);analysis=record.get('analysis',{});proposals=analysis.get('region_proposals',{})
    complete=proposals.get('complete') if isinstance(proposals,dict) else None
    result={'objects':scene['objects'],'source_size':scene['source_size'],'source_sha256':identity['source_sha256'],
            'observation_sha256':identity['observation_sha256'],'complete':complete}
    return frame(result)
