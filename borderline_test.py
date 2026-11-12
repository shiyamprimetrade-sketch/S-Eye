from math import hypot

def classify(width, height, threshold=0.78):
    points = [
        (0, 0),
        (width, 0),
        (width, height),
        (0, height)
    ]

    sides = [
        hypot(
            points[(i+1)%4][0] - points[i][0],
            points[(i+1)%4][1] - points[i][1]
        )
        for i in range(4)
    ]

    ratio = min(sides) / max(sides)

    prediction = (
        "Square" if ratio >= threshold
        else "Rectangle"
    )

    return prediction, ratio

cases = [
    (100, 100, "Square"),
    (100, 95, "Rectangle"),
    (100, 90, "Rectangle"),
    (100, 85, "Rectangle"),
    (100, 80, "Rectangle"),
    (100, 75, "Rectangle"),
    (100, 60, "Rectangle"),
    (100, 40, "Rectangle")
]

correct = 0

print("S-Eye: Borderline geometry test")

for width, height, expected in cases:
    predicted, ratio = classify(width, height)

    passed = predicted == expected
    correct += passed

    print(
        f"{width}x{height}: "
        f"ratio={ratio:.2f}, "
        f"predicted={predicted}, "
        f"expected={expected}, "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(f"Correct: {correct}/{len(cases)}")
print(
    "Accuracy:",
    round(100 * correct / len(cases), 1),
    "%"
)
