from anthill.framework.utils.singleton import Singleton
from tornado.httpclient import AsyncHTTPClient

__all__ = ['Internal', 'InternalAPIError', 'as_internal', 'api', 'InternalAPI']


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
    def as_internal(self):
        """Decorator marks function as an internal api method."""

        def decorator(func):
            setattr(self, func.__name__, func)
            return func

        return decorator


api = InternalAPI()
as_internal = api.as_internal
