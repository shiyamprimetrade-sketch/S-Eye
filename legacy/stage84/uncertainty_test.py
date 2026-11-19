def classify(ratio):
    if not 0 < ratio <= 1:
        return "Invalid"

    if ratio >= 0.95:
        return "Square-like"

    if ratio >= 0.75:
        return "Ambiguous quadrilateral"

    return "Rectangle-like"


cases = [
    ("Perfect square", 1.00, "Square-like"),
    ("95% rectangle", 0.95, "Square-like"),
    ("90% rectangle", 0.90, "Ambiguous quadrilateral"),
    ("85% rectangle", 0.85, "Ambiguous quadrilateral"),
    ("80% rectangle", 0.80, "Ambiguous quadrilateral"),
    ("Camera square", 0.80, "Ambiguous quadrilateral"),
    ("75% rectangle", 0.75, "Ambiguous quadrilateral"),
    ("60% rectangle", 0.60, "Rectangle-like"),
    ("Wide rectangle", 0.438, "Rectangle-like"),
]

passed = 0

print("S-Eye: Uncertainty-aware classification")

for name, ratio, expected in cases:
    prediction = classify(ratio)
    ok = prediction == expected
    passed += ok

    print(
        f"{name}: ratio={ratio:.3f}, "
        f"{prediction}, "
        f"{'PASS' if ok else 'FAIL'}"
    )

print()
print(f"Tests: {passed}/{len(cases)}")
print("Stage 49:", "PASS" if passed == len(cases) else "FAIL")
