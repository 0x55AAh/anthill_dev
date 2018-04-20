from concurrent.futures import ThreadPoolExecutor
from tornado.platform.asyncio import to_tornado_future
from functools import wraps
import os


class ThreadPoolExecution:
    """Tiny wrapper around ThreadPoolExecutor"""

    def __init__(self, max_workers=None, thread_name_prefix=''):
        self._max_workers = max_workers or (os.cpu_count() or 1) * 5
        self._thread_name_prefix = thread_name_prefix
        self._pool = ThreadPoolExecutor(
            max_workers=self._max_workers, thread_name_prefix=self._thread_name_prefix)

    def set_max_workers(self, count):
        if self._pool:
            self._pool.shutdown(wait=True)
        self._max_workers = count or (os.cpu_count() or 1) * 5
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def _as_future(self, blocking_func, *args, **kwargs):
        future = self._pool.submit(blocking_func, *args, **kwargs)
        return to_tornado_future(future)

    def __call__(self, blocking_func, *args, **kwargs):
        return self._as_future(blocking_func, *args, **kwargs)

    def as_future(self, blocking_func):
        @wraps(blocking_func)
        def wrapper(*args, **kwargs):
            return self._as_future(blocking_func, *args, **kwargs)
        return wrapper


thread_pool_exec = ThreadPoolExecution(
    thread_name_prefix='AnthillThreadPoolExecutor')
