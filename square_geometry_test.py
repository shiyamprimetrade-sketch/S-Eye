from math import hypot, acos, degrees

corners = [
    (160, 132),
    (207, 128),
    (213, 168),
    (163, 172)
]

def length(a, b):
    return hypot(
        b[0] - a[0],
        b[1] - a[1]
    )

def angle(a, b, c):
    u = (a[0]-b[0], a[1]-b[1])
    v = (c[0]-b[0], c[1]-b[1])

    dot = u[0]*v[0] + u[1]*v[1]

    magnitude = hypot(*u) * hypot(*v)

    cosine = max(
        -1,
        min(1, dot / magnitude)
    )

    return degrees(acos(cosine))

sides = [
    length(corners[i], corners[(i+1)%4])
    for i in range(4)
]

angles = [
    angle(
        corners[i-1],
        corners[i],
        corners[(i+1)%4]
    )
    for i in range(4)
]

print("S-Eye: Quadrilateral geometry")
print("Sides:", [round(s, 2) for s in sides])
print("Angles:", [round(a, 2) for a in angles])

print(
    "Opposite-side ratios:",
    round(min(sides[0], sides[2]) /
          max(sides[0], sides[2]), 3),
    round(min(sides[1], sides[3]) /
          max(sides[1], sides[3]), 3)
)

print(
    "Maximum angle deviation:",
    round(max(abs(a-90) for a in angles), 2)
)
