"""Bounded file snapshots and subprocess output for local prerecorded decoding.

Timeout/output limits and FFmpeg per-allocation limits are not a process sandbox
or a guarantee on total native decoder RSS.
"""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import time

MAX_VIDEO_BYTES=128*1024*1024
MAX_LOG_BYTES=64*1024
MAX_DECODED_BYTES=128*1024*1024


def hash_file(path, maximum=MAX_VIDEO_BYTES, copy_to=None):
    if type(maximum) is not int or not 1<=maximum<=MAX_VIDEO_BYTES:raise ValueError('Bounded positive byte limit required')
    digest=hashlib.sha256();count=0
    with Path(path).open('rb') as source:
        while True:
            block=source.read(min(1024*1024,maximum-count+1))
            if not block:break
            count+=len(block)
            if count>maximum:raise ValueError('Video exceeds byte limit')
            digest.update(block)
            if copy_to is not None:copy_to.write(block)
    if not count:raise ValueError('Empty video source')
    return digest.hexdigest(),count


def run_decoder(command, timeout, output_directory=None):
    """Drain to private files, poll byte/time limits, kill and reap on every error."""
    start=time.monotonic()
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
        def enforce():
            if stdout.tell()>MAX_LOG_BYTES or stderr.tell()>MAX_LOG_BYTES:
                raise ValueError('Decoder diagnostics exceed byte limit')
            if output_directory is not None:
                files=list(Path(output_directory).glob('*.png'))
                if len(files)>300 or sum(f.stat().st_size for f in files)>MAX_DECODED_BYTES:
                    raise ValueError('Decoded frame output exceeds limits')
        try:
            while process.poll() is None:
                enforce()
                if time.monotonic()-start>timeout:raise ValueError('Decoder deadline exceeded')
                time.sleep(.02)
            enforce()
            if process.returncode:raise ValueError('Local video metadata/frame decode failed')
            stdout.seek(0)
            return stdout.read(MAX_LOG_BYTES+1)
        finally:
            if process.poll() is None:process.kill()
            process.wait()
