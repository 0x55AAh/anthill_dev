from anthill.framework.core.cache import cache
from functools import wraps


def cached(timeout):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = 'test'
            return cache.get_or_set(key, func(*args, **kwargs), timeout)
        return wrapper
    return decorator
