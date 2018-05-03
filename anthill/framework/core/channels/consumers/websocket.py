from anthill.framework.core.channels.consumers.base import AsyncConsumer
from anthill.framework.core.channels.exceptions import (
    AcceptConnection, DenyConnection, InvalidChannelLayerError, StopConsumer
)
import json


class AsyncWebSocketConsumer(AsyncConsumer):
    """
    Base WebSocket consumer, async version. Provides a general encapsulation
    for the WebSocket handling model that other applications can build on.
    """

    groups = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.groups is None:
            self.groups = []

    async def websocket_connect(self, message):
        """
        Called when a WebSocket connection is opened.
        """
        try:
            for group in self.groups:
                await self.channel_layer.group_add(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")
        try:
            await self.connect()
        except AcceptConnection:
            await self.accept()
        except DenyConnection:
            await self.close()

    async def connect(self):
        await self.accept()

    async def accept(self, subprotocol=None):
        """
        Accepts an incoming socket
        """
        await super().send({"type": "websocket.accept", "subprotocol": subprotocol})

    async def websocket_receive(self, message):
        """
        Called when a WebSocket frame is received. Decodes it and passes it
        to receive().
        """
        if "text" in message:
            await self.receive(text_data=message["text"])
        else:
            await self.receive(bytes_data=message["bytes"])

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called with a decoded WebSocket frame.
        """
        pass

    async def send(self, text_data=None, bytes_data=None, close=False):
        """
        Sends a reply back down the WebSocket
        """
        if text_data is not None:
            await super().send(
                {"type": "websocket.send", "text": text_data},
            )
        elif bytes_data is not None:
            await super().send(
                {"type": "websocket.send", "bytes": bytes_data},
            )
        else:
            raise ValueError("You must pass one of bytes_data or text_data")
        if close:
            await self.close(close)

    async def close(self, code=None):
        """
        Closes the WebSocket from the server end
        """
        if code is not None and code is not True:
            await super().send(
                {"type": "websocket.close", "code": code}
            )
        else:
            await super().send(
                {"type": "websocket.close"}
            )

    async def websocket_disconnect(self, message):
        """
        Called when a WebSocket connection is closed. Base level so you don't
        need to call super() all the time.
        """
        try:
            for group in self.groups:
                await self.channel_layer.group_discard(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")
        await self.disconnect(message["code"])
        raise StopConsumer()

    async def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        pass


class AsyncJsonWebSocketConsumer(AsyncWebSocketConsumer):
    """
    Variant of AsyncWebSocketConsumer that automatically JSON-encodes and decodes
    messages as they come in and go out. Expects everything to be text; will
    error on binary data.
    """

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            await self.receive_json(await self.decode_json(text_data), **kwargs)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    async def receive_json(self, content, **kwargs):
        """
        Called with decoded JSON content.
        """
        pass

    async def send_json(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(
            text_data=await self.encode_json(content),
            close=close,
        )

    @classmethod
    async def decode_json(cls, text_data):
        return json.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content)


class WebSocketDenier(AsyncWebSocketConsumer):
    """
    Simple application which denies all requests to it.
    """

    async def connect(self):
        await self.close()
