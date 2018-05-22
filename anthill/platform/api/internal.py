from anthill.framework.utils.singleton import Singleton
from tornado.httpclient import AsyncHTTPClient
from functools import wraps

__all__ = ['Internal', 'InternalAPIError', 'internal', 'api']


class Internal(Singleton):
    """
    Implements communications between services.
    """
    def __init__(self):
        self.http_client = AsyncHTTPClient()
        super().__init__()

    def request(self):
        pass

    def get(self):
        pass

    def post(self):
        pass


class InternalAPIError(Exception):
    pass


class InternalAPI(Singleton):
    pass


api = InternalAPI()


def internal():
    """Decorator marks function as an internal api method."""
    def decorator(func):
        setattr(api, func.__name__, staticmethod(func))
        return func
    return decorator
