from anthill.framework.core.cache import cache
from anthill.framework.utils.asynchronous import thread_pool_exec as async_exec
from functools import wraps, partial
import inspect


__all__ = ['cached', 'cached_method', 'request_key_method']


def _cached(timeout, key, method=False):
    def decorator(func):
        def get_key(self):
            if callable(key):
                return key(self) if method else key()
            return key

        @wraps(func)
        def wrapper(*args, **kwargs):
            k = get_key(self=args[0])
            result = cache.get(k)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(k, result, timeout)
            return result

        @wraps(func)
        async def wrapper_async(*args, **kwargs):
            k = get_key(self=args[0])
            result = await async_exec(cache.get, k)
            if result is None:
                result = await func(*args, **kwargs)
                await async_exec(cache.set, k, result, timeout)
            return result

        if inspect.iscoroutinefunction(func):
            return wrapper_async
        else:
            return wrapper
    return decorator


cached = partial(_cached, method=False)
cached_method = partial(_cached, method=True)


def request_key_method(handler):
    request = handler.request
