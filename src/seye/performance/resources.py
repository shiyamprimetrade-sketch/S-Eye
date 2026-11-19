"""Current-process resource observations for trusted Python workloads only."""
import math,sys,time,tracemalloc


def measure(function,allocations=False):
    if not callable(function) or type(allocations) is not bool:raise ValueError('Trusted callable and boolean allocation flag required')
    owns_trace=allocations and not tracemalloc.is_tracing()
    if owns_trace:tracemalloc.start()
    wall=time.perf_counter();cpu=time.process_time()
    try:
        value=function()
        elapsed=time.perf_counter()-wall;used=time.process_time()-cpu
        ratio=used/elapsed if elapsed else None
        if ratio is not None and not math.isfinite(ratio):raise ValueError('Nonfinite CPU/wall ratio')
        allocation=tracemalloc.get_traced_memory() if owns_trace else None
        max_rss=None
        if sys.platform.startswith('linux'):
            import resource
            max_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
        report={'wall_seconds':elapsed,'process_cpu_seconds':used,'average_cpu_cores':ratio,
                'python_current_traced_bytes':allocation[0] if allocation else None,
                'python_peak_traced_bytes':allocation[1] if allocation else None,
                'allocation_measurement_owned':owns_trace,
                'allocation_skipped_reason':'pre-existing process tracing preserved' if allocations and not owns_trace else None,
                'process_lifetime_max_rss_bytes':max_rss,
                'scope':'current process including its threads; excludes children/host CPU; RSS is lifetime high-water, not workload delta',
                'portable_performance_claim':False}
        return value,report
    finally:
        if owns_trace:tracemalloc.stop()
