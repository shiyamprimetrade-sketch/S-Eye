"""Opt-in per-stage wall/process-CPU timings without changing visual evidence."""
from contextlib import contextmanager
import math,time


class Trace:
    def __init__(self):
        self.rows=[];self.wall_start=time.perf_counter();self.cpu_start=time.process_time()

    @contextmanager
    def span(self,name):
        if not isinstance(name,str) or not 1<=len(name)<=64 or len(self.rows)>=128:raise ValueError('Bounded profiling span required')
        wall=time.perf_counter();cpu=time.process_time();success=False
        try:
            yield
            success=True
        finally:
            self.rows.append({'name':name,'wall_seconds':time.perf_counter()-wall,
                              'process_cpu_seconds':time.process_time()-cpu,'success':success})

    def report(self):
        wall=time.perf_counter()-self.wall_start;cpu=time.process_time()-self.cpu_start
        return {'wall_seconds':wall,'process_cpu_seconds':cpu,'stages':[dict(row) for row in self.rows],
                'scope':'current process observation only; excludes memory persistence, child processes and host-wide CPU',
                'portable_latency_guarantee':False}
