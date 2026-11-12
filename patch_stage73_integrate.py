from pathlib import Path

path = Path("s_eye.py")
source = path.read_text()

backup = Path("s_eye_stage73_preintegration.py")

if not backup.exists():
    backup.write_text(source)

if 'choices=["analyze", "status", "isolated"]' in source:
    print("Stage 73 already integrated")
    raise SystemExit(0)

old_choices = 'choices=["analyze", "status"]'
new_choices = 'choices=["analyze", "status", "isolated"]'

if source.count(old_choices) != 1:
    raise SystemExit(
        "Unexpected command parser structure. "
        "No changes made."
    )

source = source.replace(
    old_choices,
    new_choices,
    1
)

old_arguments = '''    args = parser.parse_args()

    if args.command == "analyze":'''

new_arguments = '''    parser.add_argument(
        "--image",
        type=Path,
        help="Photograph for isolated analysis"
    )

    args = parser.parse_args()

    if args.command == "analyze":'''

if source.count(old_arguments) != 1:
    raise SystemExit(
        "Argument insertion point missing. "
        "No changes made."
    )

source = source.replace(
    old_arguments,
    new_arguments,
    1
)

old_dispatch = '''    elif args.command == "status":
        status()'''

new_dispatch = '''    elif args.command == "status":
        status()

    elif args.command == "isolated":
        if args.image is None:
            parser.error(
                "isolated requires --image PHOTO"
            )

        if args.remember:
            parser.error(
                "--remember is not yet supported "
                "for isolated analysis"
            )

        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "isolated_analysis.py"),
                "--image",
                str(args.image.expanduser().resolve())
            ],
            cwd=ROOT
        )

        raise SystemExit(result.returncode)'''

if source.count(old_dispatch) != 1:
    raise SystemExit(
        "Command dispatch structure differs. "
        "No changes made."
    )

source = source.replace(
    old_dispatch,
    new_dispatch,
    1
)

compile(source, str(path), "exec")

path.write_text(source)

print("S-Eye Stage 73: Integration installed")
print("Backup:", backup)
print("Commands: analyze, status, isolated")
