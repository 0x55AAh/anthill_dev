from .base import BaseAction
from .exceptions import ActionError
from typing import Callable, Optional, Dict, List
from tornado.template import Template
import logging
import inspect
import json


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


class CommandResult:
    def __init__(self, data: dict,
                 template_string: Optional[str] = None,
                 content_type: str = 'application/json'):
        self.content_type = content_type
        self.template_string = template_string
        self.data = data

    def __str__(self):
        return self.format()

    def __bool__(self):
        return bool(self.format())

    def format(self) -> str:
        if self.template_string is None:
            return json.dumps(self.data)
        return Template(self.template_string).generate(**self.data)


class Command:
    def __init__(self, name: str, method: Callable,
                 template_string: Optional[str] = None,
                 content_type: str = 'application/json',
                 description: Optional[str] = None):
        self.name = name
        self.method = method
        self.description = description or ''
        self.template_string = template_string
        self.content_type = content_type

    async def __call__(self, *args, **kwargs) -> CommandResult:
        try:
            if inspect.iscoroutinefunction(self.method):
                data = await self.method(*args, **kwargs)
            else:
                data = self.method(*args, **kwargs)
            return CommandResult(data, self.template_string, self.content_type)
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
                    description=kwargs.get('description', method.__doc__),
                    template_string=kwargs.get('template_string'),
                    content_type=kwargs.get('content_type', 'application/json')
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
            if result:
                # TODO: build result data
                # text = result.format()
                # content_type = result.content_type
                await emit(result)

    @as_command(template_string='Bot test command executed.',
                content_type='text/plain')
    def test(self, data: dict):
        """This is test command."""
        logger.info('Bot test command executed.')

    @as_command()
    def help(self, data: dict):
        """Get all available commands."""
        return {'help': self.commands.help()}
