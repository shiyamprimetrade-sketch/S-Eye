"""Observed geometric motion with explicit coordinate and registration assumptions."""
from math import hypot, isfinite
from statistics import median
from seye.detection.metrics import valid_box
from seye.video.temporal import finite


def motion(first, second, elapsed, registration=None):
    valid_box(first); valid_box(second)
    finite(elapsed, 'elapsed')
    if elapsed == 0: raise ValueError('Positive elapsed time required')
    shift = [((second[i]+second[i+2])-(first[i]+first[i+2]))/2 for i in (0,1)]
    correction = [0,0]
    if registration is not None:
        if not isinstance(registration,(list,tuple)) or len(registration)!=2:
            raise ValueError('Caller registration requires [dx,dy]')
        for value in registration:
            # Signed translations are allowed, but never bool/NaN/Inf.
            if type(value) not in (int,float) or not isfinite(value):
                raise ValueError('Finite registration required')
        correction=list(registration)
    residual=[shift[i]-correction[i] for i in (0,1)]
    velocity=[v/elapsed for v in shift]
    if any(not isfinite(v) for v in shift+residual+velocity) or not isfinite(hypot(*velocity)):
        raise ValueError('Motion arithmetic exceeds finite bounds')
    return {'observed_displacement':shift, 'velocity':velocity, 'elapsed_seconds':elapsed,
            'speed_pixels_per_second':hypot(*velocity),
            'size_delta':[second[i+2]-second[i]-(first[i+2]-first[i]) for i in (0,1)],
            'caller_registration':None if registration is None else correction,
            'residual_displacement':None if registration is None else residual,
            'scope':'same decoded grid; geometric correspondence assumed; no physical/semantic motion proof'}


def common_translation(pairs, elapsed):
    """Median matched-box displacement; not an automatic camera/scroll transform."""
    if not isinstance(pairs,list) or not 1<=len(pairs)<=64:
        raise ValueError('1..64 explicit correspondences required')
    values=[motion(p['before'],p['after'],elapsed)['observed_displacement'] for p in pairs]
    center=[median(v[i] for v in values) for i in (0,1)]
    return {'median_displacement':center,'support':len(values),
            'residual_distances':[hypot(v[0]-center[0],v[1]-center[1]) for v in values],
            'registration_established':False}
