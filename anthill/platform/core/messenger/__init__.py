from anthill.framework.auth.models import AnonymousUser
from anthill.platform.core.messenger.channels.handlers.websocket import WebSocketChannelHandler
from functools import wraps
import json
import six


class NotAuthenticatedError(Exception):
    pass


class AuthenticationFailedError(Exception):
    pass


def auth_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        user = self.client.user
        if user is not None and isinstance(user, AnonymousUser):
            raise NotAuthenticatedError('Authentication required')
        return await func(self, *args, **kwargs)
    return wrapper


def action(**kwargs):
    def decorator(func):
        func.action = True
        func.kwargs = kwargs
        return func
    return decorator


class BaseClient:
    def __init__(self):
        self.user = AnonymousUser()

    async def authenticate(self, user=None):
        """
        While authentication process we need to update `self.user`.
        Raise AuthenticationFailedError if failed.
        """
        if user is not None:
            self.user = user

    async def online(self):
        raise NotImplementedError

    async def create_message(self, group, message):
        raise NotImplementedError

    async def list_messages(self, group, new=None):
        raise NotImplementedError

    async def get_messages(self, group, message_ids):
        raise NotImplementedError

    async def delete_messages(self, group, message_ids):
        raise NotImplementedError

    async def update_messages(self, group, message_ids):
        raise NotImplementedError

    async def read_messages(self, group, message_ids):
        raise NotImplementedError

    async def forward_messages(self, group, message_ids, group_to):
        raise NotImplementedError


class Client(BaseClient):
    async def online(self):
        pass

    async def create_message(self, group, message):
        pass

    async def list_messages(self, group, new=None):
        pass

    async def get_messages(self, group, message_ids):
        pass

    async def delete_messages(self, group, message_ids):
        pass

    async def update_messages(self, group, message_ids):
        pass

    async def read_messages(self, group, message_ids):
        pass

    async def forward_messages(self, group, message_ids, group_to):
        pass


class MessengerHandlerMeta(type):
    def __new__(mcs, *args, **kwargs):
        handler = super().__new__(mcs, *args, **kwargs)

        handler.available_actions = {}

        for method_name in dir(handler):
            attr = getattr(handler, method_name)
            is_action = getattr(attr, 'action', False)
            if is_action:
                kwargs = getattr(attr, 'kwargs', {})
                name = kwargs.get('name', method_name)
                handler.available_actions[name] = method_name

        return handler


@six.add_metaclass(MessengerHandlerMeta)
class MessengerHandler(WebSocketChannelHandler):
    client_class = Client

    def __init__(self, *args, **kwargs):
        super(MessengerHandler, self).__init__(*args, **kwargs)
        self.client = self.get_client()

    def get_client(self):
        return self.client_class()

    async def open(self, *args, **kwargs):
        """Invoked when a new connection is opened."""
        await super(MessengerHandler, self).open(*args, **kwargs)
        await self.client.authenticate()

    async def get_groups(self):
        """Get list group names to subscribe from database."""
        return self.groups or []

    @auth_required
    async def on_channel_message(self, message):
        """Receive message from current channel."""
        await self.send(message)

    @auth_required
    async def on_message(self, message):
        """Receives message from client."""
        await self.message_handler(message)

    async def message_handler(self, message):
        message = json.loads(message)
        group_name = message.get('group')
        action_name = message.get('action')
        if group_name is None:
            raise ValueError('Message must provide a destination group')
        if action_name is None:
            raise ValueError('Message must provide an action')
        if action_name not in self.available_actions:
            raise ValueError('Action `%s` not available' % action_name)
        message.update(user=self.client.user.id)
        action_method = getattr(self, self.available_actions[action_name])
        try:
            await action_method(group_name, message)
        except Exception as e:
            # TODO: send error response
            pass

    # Client actions

    @action()
    async def create_message(self, group, message):
        await self.client.create_message(group, message)
        await self.send_to_group(group, message)

    @action()
    async def list_messages(self, group, message):
        messages = await self.client.list_messages(group, new=message.get('new'))
        msg = {
            'type': message['type'],
            'group': group,
            'data': messages,
            'user': self.client.user.id
        }
        await self.send(msg)

    @action()
    async def get_messages(self, group, message):
        message_ids = message.get('ids', [])
        messages = await self.client.get_messages(group, message_ids=message_ids)
        msg = {
            'type': message['type'],
            'group': group,
            'data': messages,
            'user': self.client.user.id
        }
        await self.send(msg)

    @action()
    async def delete_messages(self, group, message):
        message_ids = message.get('ids', [])
        await self.client.delete_messages(group, message_ids=message_ids)
        msg = {}
        await self.send_to_group(group, msg)

    @action()
    async def update_messages(self, group, message):
        message_ids = message.get('ids', [])
        await self.client.update_messages(group, message_ids=message_ids)
        msg = {}
        await self.send_to_group(group, msg)

    @action()
    async def read_messages(self, group, message):
        message_ids = message.get('ids', [])
        await self.client.read_messages(group, message_ids=message_ids)
        msg = {}
        await self.send_to_group(group, msg)

    @action()
    async def forward_messages(self, group, message):
        message_ids = message.get('ids', [])
        group_to = message.get('group_to')
        await self.client.forward_messages(
            group, message_ids=message_ids, group_to=group_to)
        msg = {}
        await self.send(msg)

    # System actions

    @action()
    async def typing_start(self, group, message):
        await self.send_to_group(group, message)

    @action()
    async def typing_finish(self, group, message):
        await self.send_to_group(group, message)
