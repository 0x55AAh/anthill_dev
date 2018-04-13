import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from tornado.platform.asyncio import to_tornado_future


class ThreadPoolExecution:
    """Tiny wrapper around ThreadPoolExecutor"""

    def __init__(self, max_workers=None):
        self._max_workers = max_workers or multiprocessing.cpu_count()
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def set_max_workers(self, count):
        if self._pool:
            self._pool.shutdown(wait=True)
        self._max_workers = count
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def _as_future(self, blocking_func, *args, **kwargs):
        future = self._pool.submit(blocking_func, *args, **kwargs)
        return to_tornado_future(future)

    def __call__(self, blocking_func, *args, **kwargs):
        return self._as_future(blocking_func, *args, **kwargs)


thread_pool_exec = ThreadPoolExecution()
