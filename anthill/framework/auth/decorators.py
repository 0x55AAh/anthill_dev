from anthill.framework.http.errors import HttpForbiddenError
import functools


def abilities_required(abilities):
    """
    Takes an ability and returns the function if the user has that ability.
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


def roles_required(roles):
    """
    Takes a role and returns the function if the user has that role.
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
