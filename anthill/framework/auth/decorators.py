from anthill.framework.http.errors import HttpForbiddenError
from anthill.framework.utils.decorators import ClassDecorator
from anthill.framework.auth.base_models import Ability
from typing import Union, List, Callable
from tornado.web import RequestHandler
from inspect import iscoroutinefunction


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
            if iscoroutinefunction(self.test_func):
                test_func_result = await self.test_func(handler.current_user)
            else:
                test_func_result = self.test_func(handler.current_user)
            if test_func_result:
                return await func(handler, *args, **kwargs)
        raise HttpForbiddenError()


user_passes_test = UserPassesTest


def ability_required(perm: Union[str, List[str]]):
    async def test_func(user):
        perms = (perm,) if isinstance(perm, str) else perm
        perms = Ability.query.filter(Ability.name.in_(perms)).all()
        return set(perms).issubset(user.abilities)
    actual_decorator = user_passes_test(test_func)
    return actual_decorator


def role_required(perm: Union[str, List[str]]):
    async def test_func(user):
        perms = (perm,) if isinstance(perm, str) else perm
        return all(map(lambda r: r in user.roles, perms))
    actual_decorator = user_passes_test(test_func)
    return actual_decorator
