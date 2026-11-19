from pathlib import Path

path = Path("s_eye.py")
source = path.read_text()

backup = Path("s_eye_stage72_backup.py")

if not backup.exists():
    backup.write_text(source)

if 'elif args.command == "isolated":' in source:
    print("Stage 73 already installed")
    raise SystemExit(0)

# Inspect the existing command parser before modifying it.
lines = source.splitlines()

print("S-Eye Stage 73: Parser inspection")

for number, line in enumerate(lines, 1):
    if (
        "add_parser" in line
        or "add_argument" in line
        or "args.command" in line
        or "parse_args" in line
    ):
        print(f"{number}: {line}")

print()
print("Inspection complete. No modifications made.")
