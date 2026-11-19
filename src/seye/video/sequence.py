"""Source-bound sequence processing, with optional verified checkpoint continuation."""
from seye.core.storage import canonical
from seye.video.continuity import ContinuityTracker
from seye.video.checkpoint import source_digest, snapshot, restore
from seye.video.performance import _track
from seye.video.summary import summarize


def observe_sequence(samples, source_sha256, config=None, checkpoint=None):
    source_digest(source_sha256)
    if len(canonical(samples))>1024*1024:raise ValueError('Sequence input exceeds 1 MiB')
    if checkpoint is not None and config is not None:raise ValueError('Cannot override checkpoint configuration')
    tracker=restore(checkpoint,source_sha256) if checkpoint is not None else ContinuityTracker(**({} if config is None else config))
    result,tracker=_track(samples,tracker)
    result.update(schema_version=1,source_sha256=source_sha256,checkpoint=snapshot(tracker,source_sha256),
                  source_binding='caller-supplied SHA-256; API does not authenticate supplied detections',
                  summary=summarize(result['frames'],source_sha256) if checkpoint is None else None,
                  summary_scope='current fresh timeline' if checkpoint is None else 'resumed chunk; full-timeline summary requires prior frames',
                  semantic_identity_proven=False,automatic_action_authorized=False)
    if len(canonical(result))>16*1024*1024:raise ValueError('Temporal evidence output exceeds 16 MiB')
    return result
