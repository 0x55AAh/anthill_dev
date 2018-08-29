from tornado.concurrent import Future, chain_future
from concurrent.futures import ThreadPoolExecutor
from tornado.process import Subprocess, cpu_count
from typing import Tuple, Union, Optional
from tornado.ioloop import IOLoop
from tornado.gen import multi
from functools import wraps
import shlex


__all__ = [
    'ThreadPoolExecution', 'thread_pool_exec', 'as_future', 'call_subprocess'
]


class ThreadPoolExecution:
    """Tiny wrapper around ThreadPoolExecutor."""

    def __init__(self, max_workers=None):
        self._max_workers = max_workers or (cpu_count() or 1) * 5
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def set_max_workers(self, count):
        if self._pool:
            self._pool.shutdown(wait=True)
        self._max_workers = count or (cpu_count() or 1) * 5
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def _as_future(self, blocking_func, *args, **kwargs):
        c_future = self._pool.submit(blocking_func, *args, **kwargs)
        t_future = Future()
        IOLoop.current().add_future(c_future, lambda f: chain_future(f, t_future))
        return t_future

    def __call__(self, blocking_func, *args, **kwargs):
        return self._as_future(blocking_func, *args, **kwargs)

    def as_future(self, blocking_func):
        @wraps(blocking_func)
        def wrapper(*args, **kwargs):
            return self._as_future(blocking_func, *args, **kwargs)
        return wrapper


thread_pool_exec = ThreadPoolExecution()
as_future = thread_pool_exec.as_future


async def call_subprocess(
        cmd: Union[str, list], stdin_data: Optional[str]=None) \
        -> Tuple[int, Union[str, bytes], Union[str, bytes]]:
    """Call sub process async."""

    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    try:
        sub_process = Subprocess(cmd,
                                 stdin=Subprocess.STREAM,
                                 stdout=Subprocess.STREAM,
                                 stderr=Subprocess.STREAM)
    except OSError as e:
        return e.errno, '', e.strerror

    if stdin_data:
        await sub_process.stdin.write(stdin_data)
        sub_process.stdin.close()

    code, result, error = await multi([
        sub_process.wait_for_exit(raise_error=False),
        sub_process.stdout.read_until_close(),
        sub_process.stderr.read_until_close()
    ])

    result = result.strip()
    error = error.strip()

    return code, result, error
