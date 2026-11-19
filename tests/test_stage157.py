import unittest,tracemalloc
from contextlib import ExitStack
from seye.performance.resources import measure
from seye.performance.trace import Trace

class ResourceProfileTests(unittest.TestCase):
    def test_cpu_allocation_scope_and_existing_tracing_preserved(self):
        value,report=measure(lambda:sum(i*i for i in range(10000)),allocations=True)
        self.assertEqual(value,sum(i*i for i in range(10000)))
        self.assertGreaterEqual(report['wall_seconds'],0);self.assertGreaterEqual(report['process_cpu_seconds'],0)
        prior=tracemalloc.is_tracing()
        if not prior:tracemalloc.start()
        try:
            _,r=measure(lambda:list(range(20)),allocations=True)
            self.assertTrue(tracemalloc.is_tracing());self.assertIsNone(r['python_peak_traced_bytes'])
            self.assertIn('pre-existing',r['allocation_skipped_reason'])
        finally:
            if not prior:tracemalloc.stop()

    def test_exception_cleanup_and_nested_span_budget(self):
        prior=tracemalloc.is_tracing()
        with self.assertRaises(RuntimeError):measure(lambda:(_ for _ in ()).throw(RuntimeError('expected')),allocations=True)
        self.assertEqual(tracemalloc.is_tracing(),prior)
        trace=Trace()
        with ExitStack() as stack:
            for _ in range(128):stack.enter_context(trace.span('nested'))
            with self.assertRaises(ValueError):stack.enter_context(trace.span('overflow'))
        self.assertEqual(len(trace.report()['stages']),128)
