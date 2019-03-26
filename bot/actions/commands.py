from .base import BaseAction
from .exceptions import ActionError
from typing import Callable
import logging
import inspect


logger = logging.getLogger('anthill.application')


def as_command(**kwargs):
    """Marks action method as action command."""

    def decorator(func):
        func.command = True
        func.kwargs = kwargs
        return func

    return decorator


class CommandError(ActionError):
    pass


class CommandNotFound(CommandError):
    pass


class CommandsAction(BaseAction):
    def __init__(self):
        self.commands = {}
        for method_name in self.__class__.__dict__:
            method = getattr(self, method_name)
            if getattr(method, 'command', False):
                kwargs = getattr(method, 'kwargs', {})
                command_name = kwargs.get('name', method_name)
                self.commands[command_name] = method

    async def on_message(self, data: dict, emit: Callable) -> None:
        try:
            command_name = data['name']
            command = self.commands[command_name]
        except KeyError:
            raise CommandNotFound
        else:
            if inspect.iscoroutinefunction(command):
                await command(data, emit)
            else:
                command(data, emit)

    @as_command()
    async def test(self, data: dict, emit: Callable) -> None:
        logger.info('Bot test command executed.')
