from pathlib import Path

path = Path("s_eye.py")
source = path.read_text()

backup = Path("s_eye_stage62_backup.py")

if not backup.exists():
    backup.write_text(source)

old = '''    for name, filename in PIPELINE:
        script = ROOT / filename'''

new = '''    outputs = {
        "local_contrast.py": "local_contrast_mask.png",
        "group_shapes.py": "grouped_shapes.png",
        "filter_regions.py": "filtered_shapes.png",
    }

    for name, filename in PIPELINE:
        output_name = outputs.get(filename)
        output_path = ROOT / output_name if output_name else None

        before_mtime = (
            output_path.stat().st_mtime_ns
            if output_path and output_path.exists()
            else None
        )

        script = ROOT / filename'''

if old not in source:
    raise SystemExit("Pipeline loop not found")

source = source.replace(old, new, 1)

old = '''        passed = process.returncode == 0

        results.append({'''

new = '''        passed = process.returncode == 0

        if passed and output_path:
            if not output_path.exists():
                print(f"ERROR: Missing output {output_name}")
                passed = False
            else:
                after_mtime = output_path.stat().st_mtime_ns

                if (
                    before_mtime is not None
                    and after_mtime <= before_mtime
                ):
                    print(
                        f"ERROR: Stale output {output_name}"
                    )
                    passed = False
                else:
                    print(
                        f"[FRESH] {output_name}"
                    )

        results.append({'''

if old not in source:
    raise SystemExit("Result validation block not found")

source = source.replace(old, new, 1)

path.write_text(source)

print("Stage 63: Output freshness checks installed")
print("Backup:", backup)
