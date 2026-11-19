"""Importable trusted test workers; never selected by public request fields."""
import os,time

def slow(request,permissions,queue):time.sleep(3)
def crash(request,permissions,queue):os._exit(7)
def wrong_identity(request,permissions,queue):
    queue.put({'schema_version':1,'request_id':'wrong','success':True,'result':{}})
