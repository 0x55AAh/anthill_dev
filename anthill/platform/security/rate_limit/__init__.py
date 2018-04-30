"""
Rate limit use general caching system.
Usage:
    from anthill.platform.security.rate_limit import default_rate_limit

    @default_rate_limit('ip', ip_address)
    def function_name():
        # function code
        ...


    def exceeded_callback(*args, **kwargs):
        # function code
        ...

    @default_rate_limit('create_room', account_id,
                        exceeded_callback=exceeded_callback, *args, **kwargs)
    def function_name():
        # function code
        ...
"""
from anthill.platform.security.rate_limit.exceptions import RateLimitException
from anthill.framework.core.cache import cache
from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string
from anthill.framework.core.exceptions import ImproperlyConfigured
from functools import wraps
import threading
import logging


logger = logging.getLogger('anthill.rate_limit')


RATE_LIMIT_ENABLE = getattr(settings, 'RATE_LIMIT_ENABLE', False)
RATE_LIMIT_CACHE_PREFIX = getattr(settings, 'RATE_LIMIT_CACHE_PREFIX', 'rl')
RATE_LIMIT_CONFIG = getattr(settings, 'RATE_LIMIT_CONFIG', {})


__all__ = ['RateLimit', 'default_rate_limit']


class RateLimitConfig(dict):
    _PERIODS = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 24 * 60 * 60,
        'w': 7 * 24 * 60 * 60
    }

    def _parse_callback(self, entry):
        callback = entry.get('callback')
        if callback is not None:
            try:
                fn = import_string(callback)
                if fn is not None and not callable(fn):
                    raise ImproperlyConfigured('Rate limit callback is not callable')
                return fn
            except ImportError:
                pass

    def _parse_rate(self, entry):
        rate = entry.get('rate')
        requests_num, raw_duration = rate.split('/')
        requests_num = int(requests_num)
        raw_duration = raw_duration.strip()
        duration_num = int(raw_duration[:-1] or 1)
        duration_unit = raw_duration[-1]
        return requests_num, duration_num * self._PERIODS[duration_unit]

    def __call__(self):
        config = {}
        for k, v in self.items():
            config[k] = dict(
                block=v.get('block'),
                callback=self._parse_callback(v),
                rate=self._parse_rate(v)
            )
        return config


class RateLimit:
    config_factory = RateLimitConfig(RATE_LIMIT_CONFIG)

    def __init__(self, storage):
        self.storage = storage
        self.config = self.config_factory()

        # Add thread safety.
        self.lock = threading.RLock()

    def __call__(self, resource_name, resource_key, exceeded_callback=None, *args, **kwargs):
        if exceeded_callback is not None and not callable(exceeded_callback):
            raise ImproperlyConfigured('Exceeded callback is not callable')

        def decorator(func):
            @wraps(func)
            def wrapper(*f_args, **f_kwargs):
                if not RATE_LIMIT_ENABLE or not RATE_LIMIT_CONFIG:
                    if not RATE_LIMIT_CONFIG:
                        logger.warning('Rate limit is not configured.')
                    return func(*f_args, **f_kwargs)
                if resource_name not in self.config:
                    logger.error('Resource %s is not configured.' % resource_name)
                    return

                rate_requests_max, rate_duration_max = self.config[resource_name]['rate']

                storage_key = self.build_storage_key(resource_name, resource_key)

                with self.lock:
                    rate_requests = self.storage.get(storage_key)
                    if rate_requests is None:
                        self.storage.set(storage_key, 1, timeout=rate_duration_max)
                    elif rate_requests < rate_requests_max:
                        self.storage.incr(storage_key)
                    else:
                        block = self.config[resource_name]['block']
                        callback = self.config[resource_name]['callback']
                        callback_kwargs = dict(
                            storage_key=storage_key,
                            rate_requests_max=rate_requests_max,
                            rate_duration=rate_duration_max,
                            rate_requests=rate_requests,
                        )
                        if block:
                            if exceeded_callback is None:
                                raise RateLimitException
                            else:
                                kwargs.update(callback_kwargs)
                                exceeded_callback(*args, **kwargs)
                                return
                        elif callback is not None:
                            callback(**callback_kwargs)
                    try:
                        return func(*f_args, **f_kwargs)
                    except Exception:
                        # Fallback first then re-raise exception
                        if rate_requests is not None and rate_requests > 0:
                            self.storage.decr(storage_key)
                        raise

            return wrapper
        return decorator

    def build_storage_key(self, resource_name, resource_key):
        return ':'.join([RATE_LIMIT_CACHE_PREFIX, resource_name, resource_key])


default_rate_limit = RateLimit(storage=cache)
