from .base import BaseAction
from .exceptions import ActionError
from typing import Callable, Optional, Dict, List
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


class CommandAlreadyRegistered(CommandError):
    pass


class Command:
    def __init__(self, name: str, method: Callable, description: str = ''):
        self.name = name
        self.method = method
        self.description = description

    async def __call__(self, *args, **kwargs):
        try:
            if inspect.iscoroutinefunction(self.method):
                return await self.method(*args, **kwargs)
            return self.method(*args, **kwargs)
        except Exception as e:
            raise CommandError from e

    def __repr__(self):
        return '<Command(name="%r", description="%r")>' % (self.name, self.description)

    def __str__(self):
        return self.name

    def help(self) -> dict:
        return {'name': self.name, 'description': self.description}


class Commands:
    def __init__(self, commands: Optional[Dict[str, Command]] = None):
        self._commands = commands or dict()

    def __iter__(self):
        return iter(self._commands)

    def __getitem__(self, item):
        return self._commands[item]

    def __str__(self):
        return str(self._commands)

    def __repr__(self):
        return repr(self._commands)

    def register(self, command: Command) -> None:
        if command.name in self._commands:
            raise CommandAlreadyRegistered
        self._commands[command.name] = command

    def unregister(self, command: Command) -> None:
        try:
            del self._commands[command.name]
        except KeyError as e:
            raise CommandNotFound from e

    def help(self) -> List[dict]:
        return list(map(lambda c: c.help(), self._commands))


class CommandsAction(BaseAction):
    def __init__(self):
        self.commands = Commands()
        for method_name in self.__class__.__dict__:
            method = getattr(self, method_name)
            if getattr(method, 'command', False):
                kwargs = getattr(method, 'kwargs', {})
                command_name = kwargs.get('name', method_name)
                command = Command(
                    name=command_name,
                    method=method,
                    description=method.__doc__
                )
                self.commands.register(command)

    async def on_message(self, data: dict, emit: Callable) -> None:
        try:
            command_name = data['name']
            command = self.commands[command_name]
        except KeyError:
            raise CommandNotFound
        else:
            result = await command(data)
            if result is not None:
                # TODO: format result
                await emit(result)

    @as_command()
    def test(self, data: dict):
        """This is test command."""
        logger.info('Bot test command executed.')

    @as_command()
    def help(self, data: dict):
        """Get all available commands."""
        return self.commands.help()
