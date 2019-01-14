from anthill.framework.conf import settings
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.handlers.socketio import SocketIOHandler
from anthill.platform.auth.handlers import UserHandlerMixin
from anthill.platform.core.messenger.handlers.client_watchers import MessengerClientsWatcher
from user_agents import parse
import socketio
import logging
import enum


logger = logging.getLogger('anthill.application')


class MessengerNamespace(socketio.AsyncNamespace):
    groups = ['__messenger__']        # Global groups. Must starts with `__` for security reason
    direct_group_prefix = '__direct'  # Must starts with `__`
    client_class = None
    is_notify_on_net_status_changed = True
    secure_direct = True
    secure_groups = True
    clients = MessengerClientsWatcher(user_limit=0)

    @enum.unique
    class NetStatus(enum.Enum):
        OFFLINE = 'offline'
        ONLINE = 'online'

    def create_client(self, user=None):
        if self.client_class is None:
            raise ImproperlyConfigured('Client class is undefined')
        return self.client_class(user=user)

    async def get_client(self, sid):
        session = await self.get_session(sid)
        return session['client']

    async def get_request_handler(self, sid):
        session = await self.get_session(sid)
        return session['request_handler']

    async def send_net_status(self, status: str) -> None:
        allowed = map(lambda x: x.value, self.NetStatus.__members__.values())
        if status not in allowed:
            raise ValueError('Status must be in %s' % allowed)

    async def build_direct_group_with(self, user_id: str, sid, reverse: bool = False) -> str:
        client = await self.get_client(sid)
        items = [self.direct_group_prefix]
        if reverse:
            items += [user_id, client.get_user_id()]
        else:
            items += [client.get_user_id(), user_id]
        return '.'.join(items)

    async def get_groups(self, sid) -> list:
        client = await self.get_client(sid)
        groups = self.groups or []
        groups += await client.get_groups() or []

        # For testing purposes
        if 'test' not in groups and settings.DEBUG:
            groups.append('test')

        # Personal group
        personal_group = client.get_personal_group()
        if personal_group not in groups:
            groups.append(personal_group)

        return groups

    def enter_groups(self, sid, groups) -> None:
        for group in groups:
            self.enter_room(sid, group)

    def leave_groups(self, sid, groups) -> None:
        for group in groups:
            self.leave_room(sid, group)

    # noinspection PyMethodMayBeStatic
    def retrieve_group(self, data):
        group = data.get('group')
        if group.startswith('__'):  # System group
            raise ValueError('Not valid group name: %s' % group)
        return group

    async def notify_on_net_status_changed(self, status: str) -> None:
        if self.is_notify_on_net_status_changed:
            await self.send_net_status(status)

    async def online(self, sid, user_id):
        """Check if user online."""
        client = await self.get_client(sid)
        group = client.get_personal_group(user_id)
        result = next(self.server.manager.get_participants(
            self.namespace, room=group), None)
        return bool(result)

    async def on_connect(self, sid, environ):
        request_handler = environ['tornado.handler']
        session = await self.get_session(sid)

        current_user = request_handler.current_user
        client = self.create_client(user=current_user)
        await client.authenticate()

        session['client'] = client
        session['request_handler'] = request_handler

        self.enter_groups(sid, await self.get_groups(sid))
        await self.notify_on_net_status_changed(self.NetStatus.ONLINE.value)

    async def on_disconnect(self, sid):
        self.leave_groups(sid, self.rooms(sid))
        await self.notify_on_net_status_changed(self.NetStatus.OFFLINE.value)

    async def on_message(self, sid, data):
        pass

    # Supported messages client can send

    # Client actions

    # GROUPS

    async def on_create_group(self, sid, data):
        client = await self.get_client(sid)

    async def on_delete_group(self, sid, data):
        client = await self.get_client(sid)
        # TODO: remove group from storage first
        # TODO: emit event to all group participants
        group = self.retrieve_group(data)
        await self.close_room(room=group)

    async def on_update_group(self, sid, data):
        client = await self.get_client(sid)

    async def on_join_group(self, sid, data):
        client = await self.get_client(sid)

    async def on_leave_group(self, sid, data):
        client = await self.get_client(sid)

    # /GROUPS

    # MESSAGES

    async def on_create_message(self, sid, data):
        content_type = data.get('content_type', 'text/plain')
        group = self.retrieve_group(data)
        data = data.get('data')
        client = await self.get_client(sid)
        message_id = await client.create_message(group, {
            'data': data,
            'content_type': content_type
        })
        content = {
            'user': {
                'id': client.get_user_id()
            },
            'content_type': content_type,
            'payload': {
                'id': message_id,
                'data': data
            }
        }
        await self.emit('create_message', data=content, room=group)

    async def on_enumerate_group(self, sid, data):
        client = await self.get_client(sid)

    async def on_get_messages(self, sid, data):
        client = await self.get_client(sid)

    async def on_delete_messages(self, sid, data):
        client = await self.get_client(sid)

    async def on_update_messages(self, sid, data):
        client = await self.get_client(sid)

    async def on_read_messages(self, sid, data):
        client = await self.get_client(sid)

    # /MESSAGES

    # /Client actions

    # System actions

    async def on_typing_started(self, sid, data):
        """Typing text message started."""
        client = await self.get_client(sid)
        group = self.retrieve_group(data)
        content = {
            'user': {
                'id': client.get_user_id()
            }
        }
        await self.emit('typing_started', data=content, room=group, skip_sid=sid)

    async def on_typing_stopped(self, sid, data):
        """Typing text message stopped."""
        client = await self.get_client(sid)
        group = self.retrieve_group(data)
        content = {
            'user': {
                'id': client.get_user_id()
            }
        }
        await self.emit('typing_stopped', data=content, room=group, skip_sid=sid)

    async def on_sending_file_started(self, sid, data):
        client = await self.get_client(sid)

    async def on_sending_file_stopped(self, sid, data):
        client = await self.get_client(sid)

    async def on_online(self, sid):
        request_handler = await self.get_request_handler(sid)
        user_agent = request_handler.request.headers.get('User-Agent')
        user_agent = parse(user_agent)
        client = await self.get_client(sid)
        data = {
            'user': {
                'id': client.get_user_id()
            },
            'device': {
                'family': user_agent.device.family,
                'brand': user_agent.device.brand,
                'model': user_agent.device.model
            },
            'os': {
                'family': user_agent.os.family,
                'version': user_agent.os.version_string
            }
        }
        # TODO: emit multiple rooms
        await self.emit('online', data=data, room=None, skip_sid=sid)

    async def on_offline(self, sid):
        client = await self.get_client(sid)
        data = {
            'user': {
                'id': client.get_user_id()
            }
        }
        # TODO: emit multiple rooms
        await self.emit('offline', data=data, room=None, skip_sid=sid)

    async def on_delivered(self, sid, data):
        pass

    # /System actions


class MessengerHandler(UserHandlerMixin, SocketIOHandler):
    def check_origin(self, origin):
        return True
        # TODO: configuration from settings.py
        # return super().check_origin(origin)
