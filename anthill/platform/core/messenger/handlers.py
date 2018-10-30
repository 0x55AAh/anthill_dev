from anthill.framework.auth.models import AnonymousUser
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.handlers.base import BaseWSClientsWatcher
from anthill.platform.core.messenger.channels.handlers.websocket import WebSocketChannelHandler
from anthill.platform.auth.handlers import UserHandlerMixin
from anthill.platform.core.messenger.exceptions import NotAuthenticatedError
from functools import wraps
import json
import enum


def auth_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        user = self.client.user
        if isinstance(user, (type(None), AnonymousUser)):
            raise NotAuthenticatedError('Authentication required')
        return await func(self, *args, **kwargs)
    return wrapper


def action(**kwargs):
    def decorator(func):
        func.action = True
        func.kwargs = kwargs
        return func
    return decorator


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


class WSClientsWatcher(BaseWSClientsWatcher):
    """Messenger handlers watcher."""
    user_limit: int = 0

    def __init__(self, user_limit: int=0):
        if user_limit:
            self.user_limit = user_limit
        self.items = {}

    # noinspection PyMethodMayBeStatic
    def get_user_id(self, handler: 'MessengerHandler') -> str:
        return handler.client.get_user_id()

    def append(self, handler: 'MessengerHandler') -> None:
        user_id = self.get_user_id(handler)
        self.items.setdefault(user_id, []).append(handler)
        if self.user_limit and len(self.items[user_id]) > self.user_limit:
            reason = ('Cannot open new connection '
                      'because of limit (%s) exceeded' % len(self.items[user_id]))
            handler.close(code=4001, reason=reason)

    def remove(self, handler: 'MessengerHandler') -> None:
        user_id = self.get_user_id(handler)
        self.items[user_id].remove(handler)

    @property
    def count(self) -> int:
        return sum(map(lambda x: len(x), self.items.values()))


class MessengerHandler(UserHandlerMixin, WebSocketChannelHandler, metaclass=MessengerHandlerMeta):
    groups = ['__messenger__']  # Global groups. Must starts with `__` for security reason
    client_class = None
    notification_on_net_status_changed = True
    direct_group_prefix = '__direct'  # Must starts with `__`
    secure_direct = True
    secure_groups = True
    ws_clients = WSClientsWatcher(user_limit=0)

    @enum.unique
    class NetStatus(enum.Enum):
        offline = 0
        online = 1

    @enum.unique
    class MessageType(enum.Enum):
        message = 0

    def __init__(self, *args, **kwargs):
        super(MessengerHandler, self).__init__(*args, **kwargs)
        self.client = None
        self.request_id = None
        self.action_name = None
        self.message_type = None

    def initialize(self, client_class=None):
        if client_class is not None:
            self.client_class = client_class
        self.client = self.get_client_instance()

    def get_client_instance(self):
        if self.client_class is None:
            raise ImproperlyConfigured('Client class is undefined')
        return self.client_class()

    async def send_personal(self, message: dict, user_id: str=None) -> None:
        group = self.client.get_personal_group(user_id=user_id)
        await self.send_to_group(group, message)

    async def send_net_status(self, status: str) -> None:
        if status not in self.NetStatus.__members__:
            raise ValueError('Status must be in %s' % list(self.NetStatus.__members__))
        friends = await self.client.get_friends() or []
        message = {
            'type': self.MessageType.message,
            'action': status,
            'user_id': self.client.get_user_id()
        }
        for friend in friends:
            group = self.client.get_personal_group(friend.id)
            await self.send_to_group(group, message)

    async def is_friend(self, user_id: str) -> bool:
        friends = await self.client.get_friends(id_only=True) or []
        return user_id in friends

    async def get_groups(self) -> list:
        """
        Get list group names to subscribe from database.
        Groups may be personal, global, general or direct.
        Personal and global groups must be system for security reason,
        for example: __messenger__, __user.12, etc.
        Direct is a system group shared for 2 persons, for example: __direct.12.512, etc.
        General group is plain group shared for 1 or more persons.
        """
        groups = await super(MessengerHandler, self).get_groups()
        groups += await self.client.get_groups() or []

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

    def build_direct_group_with(self, user_id: str, reverse: bool=False) -> str:
        items = [self.direct_group_prefix]
        if reverse:
            items += [user_id, self.client.get_user_id()]
        else:
            items += [self.client.get_user_id(), user_id]
        return '.'.join(items)

    async def open(self, *args, **kwargs) -> None:
        """Invoked when a new connection is opened."""
        await super(MessengerHandler, self).open(*args, **kwargs)
        await self.client.authenticate(user=self.current_user)
        if self.notification_on_net_status_changed:
            await self.send_net_status(self.NetStatus.online.name)

    @auth_required
    async def on_channel_message(self, message: dict) -> None:
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

        def sender_is_me():
            return self.client.get_user_id() == message['user_id']

        # DELETE GROUP
        if action_is('delete_group'):
            group = message['group']
            if group in self.get_groups():
                await self.group_discard(group)
                await self.send(message)  # Send the message only if subscribed on the group

        # UPDATE GROUP
        elif action_is('update_group'):
            old_group_name = message['group']
            new_group_name = message['data']['name']
            if old_group_name != new_group_name:
                if old_group_name in self.get_groups():  # No need in our case because we notify the group
                    await self.group_discard(old_group_name)
                    await self.group_add(new_group_name)
                    await self.send(message)  # Send the message only if subscribed on the group

        # CREATE GROUP
        elif action_is('create_group'):
            # Use in context of `send_personal` method, so no user_id checking need so far
            if sender_is_me():  # Join and notify only if message sender is me
                group = message['group']
                direct = message.get('data', {}).get('direct', False)
                if direct:
                    group_name = self.build_direct_group_with(user_id=group)  # Group is user_id if group is direct
                else:
                    group_name = group
                await self.group_add(group_name)
                await self.send(message)

        # PING MESSAGE
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

        # DEFAULT
        else:
            await self.send(message)

    @auth_required
    async def on_message(self, message: str) -> None:
        """Receives message from client."""
        await super().on_message(message)
        try:
            message = json.loads(message)
            await self.message_handler(message)
        except Exception as e:
            await self.send({
                'type': self.message_type,
                'action': self.action_name,
                'request_id': self.request_id,
                'error': str(e),
                'code': 500
            })

    async def on_connection_close(self) -> None:
        await super(MessengerHandler, self).on_connection_close()
        if self.notification_on_net_status_changed:
            await self.send_net_status(self.NetStatus.offline.name)

    async def message_handler(self, message: dict) -> None:
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

        self.message_type = message.get('type')
        if self.message_type is None:
            raise ValueError('Message must provide a type')
        if self.message_type not in self.MessageType.__members__:
            raise ValueError('Message type must be in %s' % list(self.MessageType.__members__))

        self.request_id = message.get('request_id')

        message.update(user=self.client.get_user_id())  # Add message source id

        action_method = getattr(self, self.available_actions[action_name])

        # In action method we process message, put message to channel queue
        # and send notification to the client about action status using `self.send`.
        await action_method(group_name, message)

    # Supported messages client can send

    # Client actions

    # GROUPS

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
        group_id = await self.client.create_group(group, group_data)  # Save group on database
        await self.send_personal(message)
        group_data.update(id=group_id)
        await self.send({
            'request_id': self.request_id,
            'code': 201,
            'group': group,
            'action': self.action_name,
            'type': self.message_type,
            'data': group_data
        })

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
        await self.send({
            'request_id': self.request_id,
            'code': 200,
            'group': group,
            'action': self.action_name,
            'type': self.message_type
        })

    @action()
    async def update_group(self, group: str, message: dict) -> None:
        """
        Message format:
        {
            "request_id": request_id,
            "action": "update_group",
            "type": "",
            "group": group,
            "data": {"name": new_name},
            "user_id": user_id, # Added automatically
        }
        """
        group_data = message['data']
        await self.client.update_group(group, group_data=group_data)  # Update group on database
        await self.send_to_group(group, message)
        await self.send({
            'request_id': self.request_id,
            'code': 200,
            'group': group,
            'action': self.action_name,
            'type': self.message_type,
            'data': group_data
        })

    @action()
    async def join_group(self, group: str, message: dict) -> None:
        """Join the group."""
        await self.client.join_group(group)
        await self.group_add(group)
        await self.send_to_group(group, message)
        await self.send({
            'request_id': self.request_id,
            'code': 200,
            'group': group,
            'action': self.action_name,
            'type': self.message_type
        })

    @action()
    async def leave_group(self, group: str, message: dict) -> None:
        """Leave the group."""
        await self.group_discard(group)
        await self.client.leave_group(group)
        await self.send_to_group(group, message)
        await self.send({
            'request_id': self.request_id,
            'code': 200,
            'group': group,
            'action': self.action_name,
            'type': self.message_type
        })

    # /GROUPS

    # MESSAGES

    @action()
    async def create_message(self, group: str, message: dict) -> None:
        """
        Message format:
        {
            "request_id": request_id,
            "action": "create_message",
            "type": "message",
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

    # /MESSAGES

    # PING

    @action(name='ping')
    async def ping_group(self, group: str, message: dict) -> None:
        # Hidden ping can be used to get user network status (online or offline).
        hidden = message['data'].get('hidden', False)
        reply = {
            'action': 'ping',
            'type': 'message',
            'data': {'text': 'ping', 'hidden': hidden},
            'user_id': self.client.get_user_id(),
        }
        await self.send_to_group(group, reply)

    @action(name='pong')
    async def pong_group(self, group: str, message: dict) -> None:
        reply = {
            'action': 'pong',
            'type': 'message',
            'data': {'text': 'pong'},
            'user_id': self.client.get_user_id(),
        }
        await self.send_to_group(group, reply)

    # /PING

    # /Client actions

    # System actions

    @action(system=True)
    async def typing_start(self, group: str, message: dict) -> None:
        """
        Typing text message started.
        Message format:
        {
            "action": "typing_start",
            "type": "message",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action(system=True)
    async def typing_finish(self, group: str, message: dict) -> None:
        """
        Typing text message finished.
        Message format:
        {
            "action": "typing_finish",
            "type": "message",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action(system=True)
    async def sending_file_start(self, group: str, message: dict) -> None:
        """
        Sending file uploading started.
        Message format:
        {
            "action": "sending_file_start",
            "type": "message",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action(system=True)
    async def sending_file_finish(self, group: str, message: dict) -> None:
        """
        Sending file uploading finished.
        Message format:
        {
            "action": "sending_file_finish",
            "type": "message",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action(system=True)
    async def online(self, group: str, message: dict) -> None:
        """
        User went online.
        Message format:
        {
            "action": "online",
            "type": "message",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action(system=True)
    async def offline(self, group: str, message: dict) -> None:
        """
        User went offline.
        Message format:
        {
            "action": "offline",
            "type": "message",
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    @action(system=True)
    async def delivered(self, group: str, message: dict) -> None:
        """
        Message delivered to client.
        Message format:
        {
            "action": "delivered",
            "type": "message",
            "data": {"message_id": message_id}
            "user_id": user_id,
        }
        """
        await self.send_to_group(group, message)

    # /System actions
