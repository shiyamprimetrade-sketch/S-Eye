from pathlib import Path

path = Path("s_eye.py")
source = path.read_text()

backup = Path("s_eye_stage61_backup.py")

if not backup.exists():
    backup.write_text(source)

old = '''    if args.command == "analyze":
        analyze()
        if args.remember:
            from integrate_memory import remember
            remember()
    elif args.command == "status":
        status()'''

new = '''    if args.command == "analyze":
        if args.remember:
            from source_guard import guarded_analysis
            guarded_analysis(analyze)
        else:
            analyze()
    elif args.command == "status":
        status()'''

if old not in source:
    raise SystemExit(
        "Expected command block missing. No changes made."
    )

path.write_text(source.replace(old, new, 1))

print("Stage 62: Source guard integration installed")
print("Backup:", backup)
