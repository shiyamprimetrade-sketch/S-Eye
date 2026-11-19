from math import hypot

cases = {
    "Camera square": [
        (160,132), (207,128),
        (213,168), (163,172)
    ],
    "Perfect square": [
        (0,0), (100,0),
        (100,100), (0,100)
    ],
    "Wide rectangle": [
        (0,0), (160,0),
        (160,70), (0,70)
    ]
}

expected = {
    "Camera square": "Square",
    "Perfect square": "Square",
    "Wide rectangle": "Rectangle"
}

def classify(points):
    sides = [
        hypot(
            points[(i+1)%4][0]-points[i][0],
            points[(i+1)%4][1]-points[i][1]
        )
        for i in range(4)
    ]

    ratio = min(sides) / max(sides)

    # Experimental threshold, not production-ready.
    shape = "Square" if ratio >= 0.78 else "Rectangle"

    return shape, ratio

passed = 0

print("S-Eye: Square decision experiment")

for name, points in cases.items():
    prediction, ratio = classify(points)
    correct = prediction == expected[name]

    passed += correct

    print(
        f"{name}: "
        f"{prediction}, "
        f"ratio={ratio:.3f}, "
        f"{'PASS' if correct else 'FAIL'}"
    )

print(f"Results: {passed}/{len(cases)}")

if passed != len(cases):
    raise SystemExit(1)
