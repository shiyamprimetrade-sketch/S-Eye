import unittest,threading,multiprocessing
from seye.api import Client,Permissions
from seye.integration.runner import _run
from worker_fixtures import slow,crash,wrong_identity

class WorkerLifecycleTests(unittest.TestCase):
    request={'schema_version':1,'request_id':'lifecycle','action':'analyze','image':'missing.png'}
    def test_pre_cancel_during_cancel_and_timeout_reap_workers(self):
        before={p.pid for p in multiprocessing.active_children()};event=threading.Event();event.set()
        pre=Client().request(self.request,cancel=event)
        self.assertEqual(pre['error']['type'],'Cancelled');self.assertFalse(pre['error']['partial_side_effects_possible'])
        event.clear();timer=threading.Timer(.15,event.set);timer.start()
        try:cancelled=_run(self.request,Permissions(),10,event,slow)
        finally:timer.cancel();timer.join()
        self.assertEqual(cancelled['error']['type'],'Cancelled')
        timed=_run(self.request,Permissions(),.02,None,slow)
        self.assertEqual(timed['error']['type'],'Timeout')
        self.assertFalse({p.pid for p in multiprocessing.active_children()}-before)

    def test_crash_and_wrong_response_identity_are_not_success(self):
        crashed=_run(self.request,Permissions(),10,None,crash)
        self.assertEqual(crashed['error']['type'],'WorkerExited');self.assertEqual(crashed['error']['worker_exit_code'],7)
        wrong=_run(self.request,Permissions(),10,None,wrong_identity)
        self.assertEqual(wrong['error']['type'],'InvalidResponse')
        with self.assertRaises(ValueError):Client(isolated=False).request(self.request,cancel=threading.Event())
