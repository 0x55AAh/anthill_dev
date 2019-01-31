from anthill.platform.api.internal import connector
from typing import Union
import functools
import inspect


__all__ = ['moderated']


class ModerationError(Exception):
    def __init__(self, action_types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_types = action_types


async def _run_func(func, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)


async def _check_user_action_types(handler, required_action_types):
    required_action_types = set(required_action_types)
    get_moderations = functools.partial(
        connector.internal_request, 'moderation', 'get_moderations')
    user_moderations = await get_moderations(user_id=handler.current_user.id)
    user_action_types = set(m['action_type'] for m in user_moderations)
    action_types = required_action_types.intersection(user_action_types)
    if action_types:
        raise ModerationError(action_types=action_types)


def moderated(action_types: Union[list, tuple]):
    @functools.wraps(func)
    def decorator(func):
        async def wrapper(*args, **kwargs):
            await _check_user_action_types(args[0], action_types)
            return await _run_func(func, *args, **kwargs)
        return wrapper
    return decorator
