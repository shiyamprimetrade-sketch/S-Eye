from pathlib import Path

path = Path("integrate_memory.py")
source = path.read_text()

backup = Path("integrate_memory_stage60_backup.py")

if not backup.exists():
    backup.write_text(source)

old = '''    if any(
        item.get("observation_id") == observation_id
        for item in existing
    ):
        print("S-Eye: Observation already remembered")
        print("Observation ID:", observation_id)
        return

    # Validate current records before extending memory.
    from verify_memory_v2 import verify, resolve_photo

    errors = verify(existing, resolve_photo)

    if errors:
        raise ValueError(
            "Existing memory verification failed: "
            + "; ".join(errors)
        )'''

new = '''    # Validate existing memory before any duplicate decision.
    from verify_memory_v2 import verify, resolve_photo

    errors = verify(existing, resolve_photo)

    if errors:
        raise ValueError(
            "Existing memory verification failed: "
            + "; ".join(errors)
        )

    # Stage 61 policy: one stored observation per image hash.
    # Previous duplicate records are retained for audit history.
    matching = [
        item for item in existing
        if item.get("photo_sha256") == current_hash
    ]

    if matching:
        print("S-Eye: Photograph already remembered")
        print("Photo SHA-256:", current_hash)
        print("Existing observations:", len(matching))
        print("No new memory record created")
        return'''

if old not in source:
    raise SystemExit(
        "Stage 60 code not found; no changes made"
    )

updated = source.replace(old, new, 1)

path.write_text(updated)

print("S-Eye Stage 61: Duplicate policy installed")
print("Backup:", backup)
