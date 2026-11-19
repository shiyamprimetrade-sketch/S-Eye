"""Stage 84 hull mathematics extracted unchanged for the opt-in API."""
from math import hypot

def cross(o, a, b):
    return (
        (a[0]-o[0])*(b[1]-o[1])
        - (a[1]-o[1])*(b[0]-o[0])
    )

def hull(points):
    points = sorted(set(points))
    if len(points) <= 2:
        return points

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(
            lower[-2], lower[-1], p
        ) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(
            upper[-2], upper[-1], p
        ) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

def distance(p, a, b):
    return abs(cross(a, b, p)) / max(
        hypot(b[0]-a[0], b[1]-a[1]), 1e-9
    )

def simplify(poly, tolerance):
    result = poly[:]

    while len(result) > 3:
        errors = [
            distance(
                result[i],
                result[i-1],
                result[(i+1) % len(result)]
            )
            for i in range(len(result))
        ]

        smallest = min(errors)

        if smallest > tolerance:
            break

        result.pop(errors.index(smallest))

    return result

