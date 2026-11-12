from pathlib import Path

path = Path("s_eye.py")
source = path.read_text()

backup = Path("s_eye_stage53_backup.py")

if not backup.exists():
    backup.write_text(source)

old = '''    parser.add_argument(
        "command",
        choices=["analyze", "status"]
    )'''

new = '''    parser.add_argument(
        "command",
        choices=["analyze", "status"]
    )

    parser.add_argument(
        "--remember",
        action="store_true",
        help="Save structured visual observations"
    )'''

if old not in source:
    raise SystemExit("Command parser not found")

source = source.replace(old, new, 1)

old_dispatch = '''    if args.command == "analyze":
        analyze()
    elif args.command == "status":
        status()'''

new_dispatch = '''    if args.command == "analyze":
        analyze()
        if args.remember:
            from integrate_memory import remember
            remember()
    elif args.command == "status":
        status()'''

if old_dispatch not in source:
    raise SystemExit("Command dispatch not found")

source = source.replace(
    old_dispatch,
    new_dispatch,
    1
)

path.write_text(source)

print("S-Eye Stage 60: Command integration installed")
print("Backup:", backup)
