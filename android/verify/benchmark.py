"""Measure the exact Android recognition class on S-Eye's existing held-out split."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from benchmark_independent_system import generated_dataset
from seye.integration.service import Permissions, handle


def run():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        split = generated_dataset(root)
        names = {"circle": "Circle", "triangle": "Triangle", "quadrilateral": "Quadrilateral",
                 "__unknown__": "Unknown"}
        rows = {row["path"]: names[row["label"]] for row in split["images"] if row["split"] == "test"}
        controls = {}
        for name in ("blank", "border", "cross"):
            image = Image.new("RGB", (180, 180), "white")
            draw = ImageDraw.Draw(image)
            if name == "border":
                draw.rectangle((0, 0, 60, 60), fill="black")
            elif name == "cross":
                draw.line((40, 40, 140, 140), width=6, fill="black")
                draw.line((140, 40, 40, 140), width=6, fill="black")
            key = f"control-{name}.png"
            image.save(root / key)
            controls[key] = "Unknown"
        dark_controls = {}
        for name, label in rows.items():
            inverted = f"dark-{name}"
            with Image.open(root / name) as image:
                ImageOps.invert(image.convert("RGB")).save(root / inverted)
            dark_controls[inverted] = label
        src = ROOT / "android"
        subprocess.run(["java", "-m", "jdk.compiler/com.sun.tools.javac.Main", "-d", str(root),
                        str(src / "src/online/slickk/seye/ShapeRecognizer.java"),
                        str(src / "src/online/slickk/seye/ObservationReport.java"),
                        str(src / "verify/RecognizeImages.java")], check=True)
        result = subprocess.run(
            ["java", "-cp", str(root), "RecognizeImages", *(str(root / key) for key in rows | controls | dark_controls)],
            check=True, capture_output=True, text=True)
        actual = {}
        report_file = root / "android-observation.json"
        for line in result.stdout.splitlines():
            key, payload = line.split("\t", 1)
            report_file.write_text(payload, encoding="utf-8")
            request = {"schema_version": 1, "request_id": key, "action": "android_observation",
                       "report": str(report_file), "image": str(root / key)}
            checked = handle(request, Permissions(read_roots=(root,)))
            if not checked["success"] or checked["result"]["source_bytes_match"] is not True:
                raise ValueError(f"S-Eye rejected native report for {key}: {checked}")
            actual[key] = json.loads(payload)["label"]
        expected = rows | controls | dark_controls
        if actual.keys() != expected.keys():
            raise ValueError("Missing or unexpected recognition results")
        return {"scope": "Generated original test split, inverse-polarity variants and three negative controls",
                "representative_validation": False,
                "known_correct": sum(value != "Unknown" and actual[key] == value for key, value in rows.items()),
                "known_total": sum(value != "Unknown" for value in rows.values()),
                "unknown_rejected": sum(value == "Unknown" and actual[key] == value for key, value in rows.items()),
                "unknown_total": sum(value == "Unknown" for value in rows.values()),
                "controls_passed": sum(actual[key] == value for key, value in controls.items()),
                "controls_total": len(controls),
                "inverted_polarity_matches": sum(actual[key] == value for key, value in dark_controls.items()),
                "inverted_polarity_total": len(dark_controls),
                "android_to_s_eye_reports_verified": len(actual),
                "rows": [{"file": key, "expected": value, "predicted": actual[key]} for key, value in expected.items()],
                "passed": actual == expected}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    report = json.dumps(result, indent=2) + "\n"
    print(report, end="")
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(report)
    sys.exit(0 if result["passed"] else 1)
