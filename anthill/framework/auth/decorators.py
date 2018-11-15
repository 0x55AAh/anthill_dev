from anthill.framework.http.errors import HttpForbiddenError
from typing import Union, List
import functools


def abilities_required(abilities: Union[str, List[str]]):
    """
    Takes the abilities list and returns the function if the user has that abilities.
    Raise a HttpForbiddenError exception otherwise.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.current_user:
                if isinstance(abilities, str):
                    abilities_list = (abilities,)
                else:
                    abilities_list = abilities
                if all([self.current_user.has_ability(ability) for ability in abilities_list]):
                    return func(self, *args, **kwargs)
            raise HttpForbiddenError()
        return wrapper
    return decorator


def roles_required(roles: Union[str, List[str]]):
    """
    Takes the roles list and returns the function if the user has that roles.
    Raise a HttpForbiddenError exception otherwise.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.current_user:
                if isinstance(roles, str):
                    roles_list = (roles,)
                else:
                    roles_list = roles
                if all([self.current_user.has_role(role) for role in roles_list]):
                    return func(self, *args, **kwargs)
            raise HttpForbiddenError()
        return wrapper
    return decorator
