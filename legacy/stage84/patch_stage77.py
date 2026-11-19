from pathlib import Path

path = Path("build_memory_index.py")
source = path.read_text()

backup = Path("build_memory_index_stage76_backup.py")

if not backup.exists():
    backup.write_text(source)

if "STAGE77_ATOMIC_INDEX" in source:
    print("Stage 77 already installed")
    raise SystemExit(0)

old_import = "import hashlib\n"
new_import = """import hashlib
import os
import tempfile
import fcntl
"""

if source.count(old_import) != 1:
    raise SystemExit("Unexpected imports; no changes")

source = source.replace(
    old_import,
    new_import,
    1
)

old_write = """    DESTINATION.write_text(
        json.dumps(index, indent=2)
    )"""

new_write = """    # STAGE77_ATOMIC_INDEX
    lock_path = ROOT / ".visual_memory_index.lock"

    with lock_path.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)

        temp_name = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=ROOT,
                prefix=".visual_memory_index.",
                suffix=".tmp",
                delete=False,
            ) as temp:
                temp_name = temp.name
                json.dump(index, temp, indent=2)
                temp.flush()
                os.fsync(temp.fileno())

            os.replace(temp_name, DESTINATION)
            temp_name = None

            directory_fd = os.open(
                ROOT,
                os.O_RDONLY
            )

            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)

        finally:
            if temp_name is not None:
                Path(temp_name).unlink(
                    missing_ok=True
                )

            fcntl.flock(lock, fcntl.LOCK_UN)
"""

if source.count(old_write) != 1:
    raise SystemExit(
        "Expected index writer not found; no changes"
    )

source = source.replace(
    old_write,
    new_write,
    1
)

compile(source, str(path), "exec")

path.write_text(source)

print("S-Eye Stage 77: Atomic writer installed")
print("Backup:", backup)
