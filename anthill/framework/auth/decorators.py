from anthill.framework.http.errors import HttpForbiddenError
from anthill.framework.utils.decorators import ClassDecorator
from typing import Union, List, Callable
from tornado.web import RequestHandler


class UserPassesTest(ClassDecorator):
    """
    Decorator for handler method that checks that the user
    passes the given test. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def __init__(self, test_func: Callable):
        self.test_func = test_func

    # noinspection PyMethodOverriding
    def wrapper(self, func: Callable, handler: RequestHandler, *args, **kwargs):
        if handler.current_user:
            if self.test_func(handler.current_user):
                return func(handler, *args, **kwargs)
        raise HttpForbiddenError()

    # noinspection PyMethodOverriding
    async def async_wrapper(self, func: Callable, handler: RequestHandler, *args, **kwargs):
        if handler.current_user:
            if self.test_func(handler.current_user):
                return await func(handler, *args, **kwargs)
        raise HttpForbiddenError()


user_passes_test = UserPassesTest


def permission_required(perm: Union[str, List[str]], type_: str):
    def test_func(user):
        perms = (perm,) if isinstance(perm, str) else perm
        try:
            check_method = getattr(user, 'has_' + type_)
        except AttributeError:
            raise ValueError('Permission type does not exists: %s' % type_)
        return all(map(check_method, perms))
    actual_decorator = user_passes_test(test_func)
    return actual_decorator


def ability_required(perm: Union[str, List[str]]):
    return permission_required(perm, type_='ability')


def role_required(perm: Union[str, List[str]]):
    return permission_required(perm, type_='role')
