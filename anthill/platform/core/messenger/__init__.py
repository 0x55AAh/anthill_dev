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
        if user is None or isinstance(user, AnonymousUser):
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
    personal_group_prefix = '__user'  # Must starts with `__` for security reason

    def __init__(self):
        self.user = AnonymousUser()

    async def authenticate(self, user=None):
        """
        While authentication process we need to update `self.user`.
        Raise AuthenticationFailedError if failed.
        """
        if user is not None:
            self.user = user

    def get_personal_group(self, user_id=None):
        user_id = user_id if user_id is not None else self.get_user_id()
        return ':'.join([self.personal_group_prefix, user_id])

    def get_user_id(self):
        return getattr(self.client.user, self.client.user_id_key)

    def get_user_serialized(self):
        return

    async def get_friends(self, id_only=False):
        raise NotImplementedError

    async def get_groups(self):
        raise NotImplementedError

    async def create_group(self, group_data: dict) -> str:
        raise NotImplementedError

    async def delete_group(self, group_name: str) -> None:
        raise NotImplementedError

    async def update_group(self, group_name: str, group_data: dict) -> None:
        raise NotImplementedError

    async def join_group(self, group_name: str) -> None:
        raise NotImplementedError

    async def leave_group(self, group_name: str) -> None:
        raise NotImplementedError

    async def enumerate_group(self, group: str, new=None) -> list:
        """
        List messages received from group.
        :param group: Group identifier
        :param new: Shows what messages deeded.
                    Get all messages if `None`,
                        new (not read) messages if `True`,
                        old (read) messages if `False`.
        :return: Serialized messages list
        """
        raise NotImplementedError

    async def create_message(self, group: str, message: dict) -> str:
        """
        Save message on database.
        :param group: Group identifier
        :param message: Message data
        :return: Message identifier
        """
        raise NotImplementedError

    async def get_messages(self, group: str, message_ids: list) -> list:
        """
        Get messages list by id
        :param group: Group identifier
        :param message_ids: message id list
        :return: Serialized messages list
        """
        raise NotImplementedError

    async def delete_messages(self, group: str, message_ids: list):
        """

        :param group:
        :param message_ids:
        :return:
        """
        raise NotImplementedError

    async def update_messages(self, group: str, messages_data: dict):
        """

        :param group:
        :param messages_data:
        :return:
        """
        raise NotImplementedError

    async def read_messages(self, group: str, message_ids: list):
        """

        :param group:
        :param message_ids:
        :return:
        """
        raise NotImplementedError

    async def forward_messages(self, group: str, message_ids: list, group_to: str):
        """

        :param group:
        :param message_ids:
        :param group_to:
        :return:
        """
        raise NotImplementedError


class Client(BaseClient):
    async def get_friends(self, id_only=False):
        pass

    async def get_groups(self):
        pass

    async def create_group(self, group_data):
        pass

    async def delete_group(self, group_name):
        pass

    async def update_group(self, group_name, group_data):
        pass

    async def join_group(self, group_name):
        pass

    async def leave_group(self, group_name):
        pass

    async def enumerate_group(self, group, new=None):
        pass

    async def create_message(self, group, message):
        pass

    async def get_messages(self, group, message_ids):
        pass

    async def delete_messages(self, group, message_ids):
        pass

    async def update_messages(self, group, messages_data):
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
    groups = ['__messenger__']  # Global groups. Must starts with `__` for security reason
    client_class = Client
    notification_on_net_status_changed = True
    direct_group_prefix = '__direct'  # Must starts with `__`
    secure_direct = True
    secure_groups = True
    # TODO: force wss

    def __init__(self, *args, **kwargs):
        super(MessengerHandler, self).__init__(*args, **kwargs)
        self.client = self.get_client()
        self.request_id = None
        self.action_name = None
        self.message_type = None

    def get_client(self):
        return self.client_class()

    async def send_personal(self, message, user_id=None):
        group = self.client.get_personal_group(user_id=user_id)
        await self.send_to_group(group, message)

    async def send_net_status(self, status):
        if status not in ('online', 'offline'):
            raise ValueError('Status can be `online` or `offline`')
        friends = await self.client.get_friends() or []
        message = {
            'type': '',
            'action': status,
            'user_id': self.client.get_user_id()
        }
        for friend in friends:
            group = self.client.get_personal_group(friend.id)
            await self.send_to_group(group, message)

    async def is_friend(self, user_id):
        friends = await self.client.get_friends(id_only=True) or []
        return user_id in friends

    async def get_groups(self):
        """
        Get list group names to subscribe from database.
        Groups may be personal, global, general or direct.
        Personal and global groups must be system for security reason,
        for example: __messenger__, __user:12, etc.
        Direct is a system group shared for 2 persons, for example: __direct:12:512, etc.
        General group is plain group shared for 1 or more persons.
        """
        groups = await super(MessengerHandler, self).get_groups()
        groups += await self.client.get_groups()

        # Personal group
        personal_group = self.client.get_personal_group()
        if personal_group not in groups:
            groups.append(personal_group)

        # Direct groups
        friends = await self.client.get_friends() or []
        for friend in friends:
            _gg = self.build_direct_group_with(friend.id, reverse=True)
            if _gg not in groups:
                groups.append(_gg)

        return groups

    @classmethod
    def is_group_system(cls, group: str) -> bool:
        return group.startswith('__')

    def build_direct_group_with(self, user_id, reverse=False):
        if reverse:
            return ':'.join([self.direct_group_prefix, user_id, self.client.get_user_id()])
        return ':'.join([self.direct_group_prefix, self.client.get_user_id(), user_id])

    async def open(self, *args, **kwargs):
        """Invoked when a new connection is opened."""
        await super(MessengerHandler, self).open(*args, **kwargs)
        await self.client.authenticate()
        if self.notification_on_net_status_changed:
            self.send_net_status('online')

    @auth_required
    async def on_channel_message(self, message):
        """
        Receive message from current channel.
        If there is need for message pre-processing we can
        do it right here, for example:
        ```
        if action_is(specific_action):
             do_some_work()
        ```
        """
        def action_is(action_name):
            return message['action'] == action_name

        if action_is('delete_group'):
            group = message['group']
            if group in self.get_groups():
                await self.channel_layer.group_discard(group, self.channel_name)
                await self.send(message)  # Send the message only if subscribed on the group
        elif action_is('update_group'):
            old_group_name = message['group']
            new_group_name = message['data']['name']
            group_name_changed = old_group_name != new_group_name
            if group_name_changed:
                if old_group_name in self.get_groups():  # No need in our case because we notify the group
                    await self.channel_layer.group_discard(old_group_name, self.channel_name)
                    await self.channel_layer.group_add(new_group_name, self.channel_name)
                    await self.send(message)  # Send the message only if subscribed on the group
        elif action_is('ping'):
            # We can send message to client to answer with `pong`.
            # Also we can answer with `pong` right here (hidden ping).
            # Hidden ping can be used to get user network status (online or offline).
            hidden = message['data'].get('hidden', False)
            if hidden:
                message['data'].update(text='pong')
                await self.send_personal(message, user_id=message['user_id'])
            else:
                await self.send(message)
        else:
            await self.send(message)

    @auth_required
    async def on_message(self, message):
        """Receives message from client."""
        await self.message_handler(message)

    async def on_connection_close(self):
        super(MessengerHandler, self).on_connection_close()
        if self.notification_on_net_status_changed:
            self.send_net_status('offline')

    async def message_handler(self, message):
        message = json.loads(message)

        group_name = message.get('group')
        if group_name is None:
            raise ValueError('Message must provide a destination group')
        if self.is_group_system(group_name):  # Message group name cannot be system
            raise ValueError('Not valid group name: %s' % group_name)

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
    async def create_group(self, group: str, message: dict) -> None:
        """
        Message format:
        {
            "request_id": request_id,
            "action": "create_group",
            "type": "",
            "group": group, # Destination user_id if group is direct
            "data": {"direct": False},
            "user_id": user_id, # Added automatically
        }
        """
        group_data = message['data']
        direct = group_data.get('direct', False)
        await self.client.create_group(group_data)  # Save group on database
        if direct:
            user_id = message['group']  # user_id if group is direct
            group_name = self.build_direct_group_with(user_id)
        else:
            group_name = group
        await self.channel_layer.group_add(group_name, self.channel_name)  # Subscribe on the created group
        reply = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'data': {'name': group_name, 'direct': direct}
        }
        await self.send(reply)

    @action()
    async def delete_group(self, group: str, message: dict) -> None:
        """
        Message format:
        {
            "request_id": request_id,
            "action": "delete_group",
            "type": "",
            "group": group, # Destination user_id if group is direct
            "user_id": user_id, # Added automatically
        }
        """
        await self.send_to_global_groups(message)  # Notify all user channels about the group deletion
        await self.client.delete_group(group)      # Finally delete the group from database

    @action()
    async def update_group(self, group: str, message: dict) -> None:
        """
        Message format:
        {
            "request_id": request_id,
            "action": "update_group",
            "type": "",
            "group": group, # Destination user_id if group is direct
            "data": {"name": new_name, "direct": False},
            "user_id": user_id, # Added automatically
            "direct": True
        }
        """
        group_data = message['data']
        await self.client.update_group(group, group_data=group_data)
        await self.send_to_group(group, message)

    @action()
    async def join_group(self, group: str, message: dict) -> None:
        await self.client.join_group(group)
        await self.channel_layer.group_add(group, self.channel_name)
        await self.send(message)

    @action()
    async def leave_group(self, group: str, message: dict) -> None:
        await self.channel_layer.group_discard(group, self.channel_name)
        await self.client.leave_group(group)
        await self.send(message)

    @action()
    async def create_message(self, group: str, message: dict) -> None:
        """
        Message format:
        {
            "request_id": request_id,
            "action": "create_message",
            "type": "",
            "group": group, # Destination user_id if message is direct
            "data": {"content": content, "binary": False, "draft": False},
            "user_id": user_id, # Added automatically
            "direct": True
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
            direct = message.get('direct', False)
            if direct:
                # Group is destination user_id
                group = self.build_direct_group_with(group)
            await self.send_to_group(group, message)

    @action()
    async def enumerate_group(self, group: str, message: dict) -> None:
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
    async def get_messages(self, group: str, message: dict) -> None:
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
    async def delete_messages(self, group: str, message: dict) -> None:
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
    async def update_messages(self, group: str, message: dict) -> None:
        """
        Data format:
        {
            "data": {
                "message_id": {"content": content, "binary": False, "draft": False},
                ...
            }
        }
        """
        messages_data = message.get('data', {})
        messages = await self.client.update_messages(group, messages_data=messages_data)
        payload = {
            'request_id': self.request_id,
            'action': self.action_name,
            'type': self.message_type,
            'user_id': self.client.get_user_id(),
            'data': messages
        }
        await self.send_to_group(group, payload)

    @action()
    async def read_messages(self, group: str, message: dict) -> None:
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
    async def forward_messages(self, group: str, message: dict) -> None:
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
    async def ping_group(self, group: str, message: dict) -> None:
        # Hidden ping can be used to get user network status (online or offline).
        hidden = message['data'].get('hidden', False)
        reply = {
            'action': 'ping',
            'type': '',
            'data': {'text': 'ping', 'hidden': hidden},
            'user_id': self.client.get_user_id(),
        }
        await self.send_to_group(group, reply)

    @action(name='pong')
    async def pong_group(self, group: str, message: dict) -> None:
        reply = {
            'action': 'pong',
            'type': '',
            'data': {'text': 'pong'},
            'user_id': self.client.get_user_id(),
        }
        await self.send_to_group(group, reply)

    # System actions

    @action()
    async def typing_start(self, group: str, message: dict) -> None:
        """
        Typing text message started.
        Message format:
        {
            "action": "typing_start",
            "type": "",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def typing_finish(self, group: str, message: dict) -> None:
        """
        Typing text message finished.
        Message format:
        {
            "action": "typing_finish",
            "type": "",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def sending_file_start(self, group: str, message: dict) -> None:
        """
        Sending file uploading started.
        Message format:
        {
            "action": "sending_file_start",
            "type": "",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def sending_file_finish(self, group: str, message: dict) -> None:
        """
        Sending file uploading finished.
        Message format:
        {
            "action": "sending_file_finish",
            "type": "",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def online(self, group: str, message: dict) -> None:
        """
        User went online.
        Message format:
        {
            "action": "online",
            "type": "",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action()
    async def offline(self, group: str, message: dict) -> None:
        """
        User went offline.
        Message format:
        {
            "action": "offline",
            "type": "",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)
