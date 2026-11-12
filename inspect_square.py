from pathlib import Path

source = Path("classify_camera.py").read_text()

source = source.replace(
    "scale * 0.04",
    "scale * 0.08"
)

needle = '    if count == 3:'

diagnostics = '''
    if i == 2:
        print("SQUARE DIAGNOSTICS")
        print("Corners:", corners)

        if count == 4:
            sides = [
                hypot(
                    corners[(j+1)%4][0]-corners[j][0],
                    corners[(j+1)%4][1]-corners[j][1]
                )
                for j in range(4)
            ]

            print(
                "Side lengths:",
                [round(s, 2) for s in sides]
            )

            print(
                "Side ratio:",
                round(min(sides)/max(sides), 3)
            )

'''

source = source.replace(
    needle,
    diagnostics + needle,
    1
)

Path("inspect_square_runner.py").write_text(source)

print("Diagnostic runner created")
