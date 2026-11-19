"""Read-only tool preflight detects ordinary path replacement, not all OS races."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReadPlan:
    rows: tuple

    def check(self,permissions):
        for source,expected,signature in self.rows:
            target=permissions.require(source)
            if str(target)!=expected or not target.is_file():raise PermissionError('Read target changed since preflight')
            stat=target.stat();actual=(stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns)
            if actual!=signature:raise PermissionError('Read source metadata changed since preflight')
        return True


def plan_reads(request,permissions):
    paths=[request[key] for key in ('image','model','memory','previous') if request.get(key) is not None]
    for template in request.get('templates',[]):paths.append(template['path'])
    if len(paths)>12:raise ValueError('Tool read path budget exceeded')
    rows=[]
    for source in paths:
        target=permissions.require(source)
        if not target.is_file():raise ValueError('Read tool requires an existing regular file')
        stat=target.stat();maximum=256*1024*1024 if source==request.get('memory') else 32*1024*1024
        if stat.st_size>maximum:raise ValueError('Tool source exceeds byte budget')
        rows.append((str(source),str(target),(stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns)))
    return ReadPlan(tuple(rows))
