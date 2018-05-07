from anthill.platform.core.messenger.channels.exceptions import InvalidChannelLayerError


class ChannelHandlerMixin:
    groups = None

    async def get_groups(self):
        """Returns group names."""
        return self.groups or []

    async def channel_receive_callback(self):
        if self.channel_receive:
            while True:
                message = await self.channel_receive()
                await self.on_channel_message(message)

    async def on_channel_message(self, message):
        """Receives message from current channel."""

    async def on_message(self, message):
        """Receives message from client."""

    async def send_to_channel(self, channel, message):
        """Sends the given message to the given channel."""
        try:
            await self.channel_layer.send(channel, message)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")

    async def send_to_group(self, group, message):
        """Sends the given message to the given group."""
        try:
            await self.channel_layer.group_send(group, message)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")

    async def send_to_global_groups(self, message):
        global_groups = self.groups or []
        for group in global_groups:
            await self.send_to_group(group, message)
