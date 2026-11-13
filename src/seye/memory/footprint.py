"""Read-only storage accounting and exclusive verified SQLite backup recovery."""
import hashlib,math,os,sqlite3,tempfile,time
from pathlib import Path
from seye.memory.store import Memory
from seye.memory.transfer import history_events

MAX_SNAPSHOT_BYTES=256*1024*1024


def storage_report(memory):
    memory.db.execute('SAVEPOINT seye_storage_report')
    try:
        count=memory.db.execute('SELECT COUNT(*) FROM observations').fetchone()[0]
        if count>10000:raise ValueError('Storage report inventory exceeds 10000 observations')
        memory.verify();size=memory.db.execute('PRAGMA page_size').fetchone()[0]
        pages=memory.db.execute('PRAGMA page_count').fetchone()[0];free=memory.db.execute('PRAGMA freelist_count').fetchone()[0]
        payload=memory.db.execute('SELECT COALESCE(SUM(LENGTH(CAST(payload AS BLOB))),0) FROM observations').fetchone()[0]
        ids={r[0] for r in memory.db.execute('SELECT id FROM observations')};history=history_events(memory,ids)
        index_bytes=0
        if memory.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='seye_packet_trees'").fetchone():
            index_bytes=memory.db.execute('SELECT COALESCE(SUM(LENGTH(CAST(payload AS BLOB))),0) FROM seye_packet_trees').fetchone()[0]
        files=[]
        for suffix in ('','-wal','-shm'):
            path=Path(str(memory.path)+suffix)
            if path.is_file():files.append({'kind':'database' if not suffix else suffix[1:],'file_bytes':path.stat().st_size})
        return {'observations':count,'history_events':len(history),'observation_payload_bytes':payload,'derived_index_payload_bytes':index_bytes,
                'sqlite_page_bytes':size*pages,'sqlite_freelist_bytes':size*free,'files':files,
                'scope':'SQLite/file byte accounting, not process RAM or guaranteed reclaimable disk; no vacuum/write performed'}
    finally:memory.db.execute('RELEASE SAVEPOINT seye_storage_report')


def _digest(path):
    digest=hashlib.sha256();total=0
    with Path(path).open('rb') as stream:
        while block:=stream.read(1024*1024):
            total+=len(block)
            if total>MAX_SNAPSHOT_BYTES:raise ValueError('Snapshot exceeds 256 MiB')
            digest.update(block)
    return digest.hexdigest()


def verify_snapshot(path,expected_sha256):
    if not isinstance(expected_sha256,str) or len(expected_sha256)!=64 or any(c not in '0123456789abcdef' for c in expected_sha256):raise ValueError('Snapshot SHA-256 required')
    if _digest(path)!=expected_sha256:raise ValueError('Snapshot digest mismatch')
    restored=Memory(path,read_only=True)
    try:
        result=restored.verify();ids={r[0] for r in restored.db.execute('SELECT id FROM observations')}
        if len(ids)>10000:raise ValueError('Snapshot inventory exceeds 10000 observations')
        events=history_events(restored,ids)
    finally:restored.close()
    if _digest(path)!=expected_sha256:raise ValueError('Snapshot changed during verification')
    return dict(result,history_events=len(events),snapshot_sha256=expected_sha256)


def snapshot(memory,destination,timeout=10):
    if type(timeout) not in (int,float) or not math.isfinite(timeout) or not 0<timeout<=60:raise ValueError('Backup timeout must be in (0,60]')
    if memory.db.in_transaction:raise ValueError('Finish caller transaction before snapshot backup')
    memory.verify();pages=memory.db.execute('PRAGMA page_count').fetchone()[0];size=memory.db.execute('PRAGMA page_size').fetchone()[0]
    if pages*size>MAX_SNAPSHOT_BYTES:raise ValueError('Snapshot exceeds 256 MiB')
    destination=Path(destination)
    if destination.exists() or destination.is_symlink():raise FileExistsError('Snapshot never overwrites a destination')
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.seye-snapshot-',suffix='.sqlite3',dir=destination.parent);os.close(fd);temporary=Path(name)
    target=None;start=time.monotonic()
    try:
        target=sqlite3.connect(temporary)
        def progress(status,remaining,total):
            if time.monotonic()-start>timeout:raise TimeoutError('Snapshot backup deadline exceeded')
            if total*size>MAX_SNAPSHOT_BYTES or temporary.stat().st_size>MAX_SNAPSHOT_BYTES:raise ValueError('Snapshot exceeds 256 MiB')
        memory.db.backup(target,pages=64,progress=progress,sleep=.01);target.close();target=None
        with temporary.open('r+b') as stream:os.fsync(stream.fileno())
        digest=_digest(temporary);result=verify_snapshot(temporary,digest)
        os.link(temporary,destination)
        return dict(result,snapshot_bytes=destination.stat().st_size,derived_indexes_preserved=True,
                    scope='consistent SQLite backup/reopen; checksums detect mismatch, not authenticity; stale derived indexes still require rebuild')
    finally:
        if target is not None:target.close()
        temporary.unlink(missing_ok=True)
