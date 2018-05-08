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
    user_id_key = 'id'
    personal_group_prefix = '__user'

    def __init__(self):
        self.user = AnonymousUser()

    async def authenticate(self, user=None):
        """
        While authentication process we need to update `self.user`.
        Raise AuthenticationFailedError if failed.
        """
        if user is not None:
            self.user = user

    def get_personal_group(self):
        return ':'.join([self.personal_group_prefix, self.get_user_id()])

    def get_user_id(self):
        return getattr(self.client.user, self.client.user_id_key)

    def get_user_serialized(self):
        return

    async def get_friends(self):
        raise NotImplementedError

    async def get_groups(self):
        raise NotImplementedError

    async def online(self):
        raise NotImplementedError

    async def create_message(self, group, message):
        """Save message on database"""
        raise NotImplementedError

    async def enumerate_group(self, group, new=None):
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
    async def get_friends(self):
        pass

    async def get_groups(self):
        pass

    async def online(self):
        pass

    async def create_message(self, group, message):
        pass

    async def enumerate_group(self, group, new=None):
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
    groups = ['__messenger__']  # Global groups
    client_class = Client
    notification_on_join = True
    # TODO: force wss

    def __init__(self, *args, **kwargs):
        super(MessengerHandler, self).__init__(*args, **kwargs)
        self.client = self.get_client()
        self.request_id = None
        self.action_name = None
        self.message_type = None

    def get_client(self):
        return self.client_class()

    async def send_personal(self, message):
        group = self.client.get_personal_group()
        await self.send_to_group(group, message)

    async def get_groups(self):
        """Get list group names to subscribe from database."""
        groups = await super(MessengerHandler, self).get_groups()
        groups += await self.client.get_groups()

        # Subscribe on personal group
        personal_group = self.client.get_personal_group()
        if personal_group not in groups:
            groups.append(personal_group)

        return groups

    async def open(self, *args, **kwargs):
        """Invoked when a new connection is opened."""
        await super(MessengerHandler, self).open(*args, **kwargs)
        await self.client.authenticate()
        if self.notification_on_join:
            friends = await self.client.get_friends() or []
            message = {
                'type': '',
                'action': '',
                'user_id': self.client.get_user_id()
            }
            for friend in friends:
                group = ':'.join([self.client.personal_group_prefix, friend.id])
                await self.send_to_group(group, message)

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
        if group_name is None:
            raise ValueError('Message must provide a destination group')

        action_name = message.get('action')
        if action_name is None:
            raise ValueError('Message must provide an action')
        if action_name not in self.available_actions:
            raise ValueError('Action `%s` not available' % action_name)
        self.action_name = action_name

        self.message_type = message['type']
        self.request_id = message.get('request_id')

        message.update(user=self.client.get_user_id())  # Add message source id

        action_method = getattr(self, self.available_actions[action_name])
        try:
            await action_method(group_name, message)
        except Exception as e:
            reply = {
                'type': self.message_type,
                'action': self.action_name,
                'request_id': self.request_id,
                'errors': str(e)
            }
            self.send(reply)

    # Client actions

    @action()
    async def create_message(self, group, message):
        """
        Message format:
        {
            "request_id": request_id,
            "action": action_name,
            "type": message_type,
            "group": group,
            "data": {"content": content, "binary": False, "draft": False},
            "user_id": user_id, # Added automatically
        }
        """
        if not message.get('data', {}).get('content'):
            raise ValueError('Message must provide content data')
        message_id = await self.client.create_message(group, message)  # Save message on database
        message.update(id=message_id)
        draft = message.get('data', {}).get('draft')
        if draft:
            await self.send_personal(message)
        else:
            await self.send_to_group(group, message)

    @action()
    async def enumerate_group(self, group, message):
        messages = await self.client.enumerate_group(group, new=message.get('new'))
        reply = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'group': group,
            'data': messages
        }
        await self.send(reply)

    @action()
    async def get_messages(self, group, message):
        message_ids = message.get('ids', [])
        messages = await self.client.get_messages(group, message_ids=message_ids)
        reply = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'group': group,
            'data': messages
        }
        await self.send(reply)

    @action()
    async def delete_messages(self, group, message):
        message_ids = message.get('ids', [])
        await self.client.delete_messages(group, message_ids=message_ids)
        payload = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'user_id': self.client.get_user_id(),
        }
        await self.send_to_group(group, payload)

    @action()
    async def update_messages(self, group, message):
        message_ids = message.get('ids', [])
        messages = await self.client.update_messages(group, message_ids=message_ids)
        payload = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'user_id': self.client.get_user_id(),
            'data': messages
        }
        await self.send_to_group(group, payload)

    @action()
    async def read_messages(self, group, message):
        message_ids = message.get('ids', [])
        await self.client.read_messages(group, message_ids=message_ids)
        payload = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'user_id': self.client.get_user_id(),
        }
        await self.send_to_group(group, payload)

    @action()
    async def forward_messages(self, group, message):
        message_ids = message.get('ids', [])
        group_to = message.get('group_to')
        await self.client.forward_messages(group, message_ids=message_ids, group_to=group_to)
        reply = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'group': group,
        }
        await self.send(reply)

    @action(name='ping')
    async def ping_group(self, group, message):
        reply = {
            'action': 'ping',
            'type': '',
            'data': {'text': 'pong'},
            'user_id': self.client.get_user_id(),
        }
        await self.send_to_group(group, reply)

    # System actions

    @action()
    async def typing_start(self, group, message):
        """
        Message format:
        {
            "action": action_name,
            "type": message_type,
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def typing_finish(self, group, message):
        """
        Message format:
        {
            "action": action_name,
            "type": message_type,
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def sending_file_start(self, group, message):
        """
        Message format:
        {
            "action": action_name,
            "type": message_type,
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def sending_file_finish(self, group, message):
        """
        Message format:
        {
            "action": action_name,
            "type": message_type,
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)
