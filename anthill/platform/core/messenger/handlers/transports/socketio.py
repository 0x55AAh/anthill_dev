from anthill.framework.handlers.socketio import SocketIOHandler
from anthill.platform.core.messenger.handlers.client_watchers import MessengerClientsWatcher
import socketio


class MessengerNamespace(socketio.AsyncNamespace):
    groups = ['__messenger__']  # Global groups. Must starts with `__` for security reason
    client_class = None
    notification_on_net_status_changed = True
    clients = MessengerClientsWatcher(user_limit=0)

    def on_connect(self, sid, environ):
        pass

    def on_disconnect(self, sid):
        pass

    # Supported messages client can send

    # Client actions

    # GROUPS

    async def on_create_group(self, sid, data):
        pass

    async def on_delete_group(self, sid, data):
        pass

    async def on_update_group(self, sid, data):
        pass

    async def on_join_group(self, sid, data):
        pass

    async def on_leave_group(self, sid, data):
        pass

    # /GROUPS

    # MESSAGES

    async def on_create_message(self, sid, data):
        pass

    async def on_enumerate_group(self, sid, data):
        pass

    async def on_get_messages(self, sid, data):
        pass

    async def on_delete_messages(self, sid, data):
        pass

    async def on_update_messages(self, sid, data):
        pass

    async def on_read_messages(self, sid, data):
        pass

    async def on_forward_messages(self, sid, data):
        pass

    # /MESSAGES

    # PING

    async def on_ping_group(self, sid, data):
        pass

    async def on_pong_group(self, sid, data):
        pass

    # /PING

    # /Client actions

    # System actions

    async def on_typing_start(self, sid, data):
        pass

    async def on_typing_finish(self, sid, data):
        pass

    async def on_sending_file_start(self, sid, data):
        pass

    async def on_sending_file_finish(self, sid, data):
        pass

    async def on_online(self, sid, data):
        pass

    async def on_offline(self, sid, data):
        pass

    async def on_delivered(self, sid, data):
        pass

    # /System actions


class MessengerHandler(SocketIOHandler):
    def check_origin(self, origin):
        return True
        # TODO: configuration from settings.py
        # return super().check_origin(origin)
