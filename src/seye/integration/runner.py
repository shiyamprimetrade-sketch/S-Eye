"""Killable worker lifecycle with deadline, cancellation and crash reporting.

Cleanup is bounded separately from the work deadline. Committed side effects may
remain; termination is not a native child-process-tree sandbox.
"""
import math,multiprocessing,time
from queue import Empty
from seye.core.storage import canonical
from seye.integration.contracts import validate_response,json_value


def failure(request,kind,message,**details):
    return {'schema_version':1,'request_id':request.get('request_id') if isinstance(request,dict) else None,
            'success':False,'error':dict(type=kind,message=message,**details)}


def _worker(request,permissions,queue):
    from seye.integration.service import handle
    response=handle(request,permissions)
    try:json_value(response,16*1024*1024)
    except (ValueError,TypeError):response=failure(request,'ResponseLimit','Worker response violates bounded JSON contract')
    queue.put(response)


def run(request,permissions,timeout=30,cancel=None):
    return _run(request,permissions,timeout,cancel,_worker)


def _run(request,permissions,timeout,cancel,worker):
    if type(timeout) not in (int,float) or not math.isfinite(timeout) or not 0<timeout<=120:raise ValueError('Request timeout must be in (0,120] seconds')
    if cancel is not None and not callable(getattr(cancel,'is_set',None)):raise ValueError('Cancellation event must provide is_set()')
    if len(canonical(request))>1024*1024:raise ValueError('Integration request exceeds 1 MiB')
    if cancel is not None and cancel.is_set():return failure(request,'Cancelled','Request cancelled before worker startup',partial_side_effects_possible=False)
    deadline=time.monotonic()+timeout;context=multiprocessing.get_context('spawn')
    queue=context.Queue(maxsize=1);process=context.Process(target=worker,args=(request,permissions,queue));started=False
    try:
        if time.monotonic()>=deadline:return failure(request,'Timeout','Request deadline exceeded before worker startup',partial_side_effects_possible=False)
        process.start();started=True
        while True:
            if cancel is not None and cancel.is_set():return failure(request,'Cancelled','Request cancelled; committed writes are not undone',partial_side_effects_possible=True)
            remaining=deadline-time.monotonic()
            if remaining<=0:return failure(request,'Timeout','Request deadline exceeded; committed writes are not undone',partial_side_effects_possible=True)
            try:response=queue.get(timeout=min(.05,remaining))
            except Empty:
                if process.is_alive():continue
                try:response=queue.get(timeout=min(.05,max(0,deadline-time.monotonic())))
                except Empty:return failure(request,'WorkerExited','Worker exited without a response',worker_exit_code=process.exitcode,partial_side_effects_possible=True)
            try:return validate_response(response,request.get('request_id') if isinstance(request,dict) else None)
            except (ValueError,TypeError):return failure(request,'InvalidResponse','Worker response contract or identity mismatch',partial_side_effects_possible=True)
    except KeyboardInterrupt:
        return failure(request,'Cancelled','Request interrupted; committed writes are not undone',partial_side_effects_possible=started)
    finally:
        if started:
            process.join(timeout=.1)
            if process.is_alive():process.terminate();process.join(timeout=2)
            if process.is_alive():process.kill();process.join(timeout=2)
        queue.close();queue.cancel_join_thread()
