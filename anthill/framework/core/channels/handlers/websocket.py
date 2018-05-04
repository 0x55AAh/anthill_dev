from anthill.framework.handlers import WebSocketHandler
from anthill.framework.core.channels.handlers.base import ChannelHandlerMixin
from anthill.framework.core.channels.exceptions import InvalidChannelLayerError
from anthill.framework.core.channels.layers import get_channel_layer
from tornado.ioloop import IOLoop
import functools


class WebSocketChannelHandler(ChannelHandlerMixin, WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        IOLoop.current().add_callback(self.channel_receive_callback)

        self.channel_layer = None
        self.channel_name = None
        self.channel_receive = None

    async def open(self, *args, **kwargs):
        """Invoked when a new WebSocket is opened."""
        # Initialize channel layer
        self.channel_layer = get_channel_layer()
        if self.channel_layer is not None:
            self.channel_name = await self.channel_layer.new_channel()
            self.channel_receive = functools.partial(self.channel_layer.receive, self.channel_name)
        # Add channel groups
        groups = await self.get_groups()
        try:
            for group in groups:
                await self.channel_layer.group_add(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")

    async def send(self, message, binary=False, close=None, reason=None):
        """
        Sends the given message to the client of this Web Socket.
        """
        self.write_message(message, binary=binary)
        if close is not None:
            await self.close(close, reason)

    async def receive(self, message):
        """Receives message from current channel"""
        pass

    async def on_message(self, message):
        """
        Standard WebSockets message source method.
        Use `self.receive` instead.
        """
        pass

    async def on_connection_close(self):
        # Remove channel groups
        try:
            for group in self.groups:
                await self.channel_layer.group_discard(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")
        super().on_connection_close()

    def on_close(self):
        """Invoked when the WebSocket is closed."""


class JsonWebSocketChannelHandler(WebSocketChannelHandler):
    async def send_json(self, message, close=None, reason=None):
        """
        Encode the given message as JSON and send it to the client.
        """
        await super().send(
            message=await self.encode_json(message),
            close=close,
            reason=reason
        )

    async def receive(self, message):
        """
        Decode JSON message to dict and pass it to receive_json method.
        """
        if message:
            await self.receive_json(await self.decode_json(message))
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    async def receive_json(self, message):
        """Receives message from current channel"""
        pass

    @classmethod
    async def decode_json(cls, message):
        return json.loads(message)

    @classmethod
    async def encode_json(cls, message):
        return json.dumps(message)
