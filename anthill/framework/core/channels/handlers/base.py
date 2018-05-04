from anthill.framework.core.channels.exceptions import InvalidChannelLayerError


class ChannelHandlerMixin:
    groups = None

    async def get_groups(self):
        """Returns group names."""
        return self.groups or []

    async def channel_receive_callback(self):
        if self.channel_receive:
            while True:
                message = await self.channel_receive()
                await self.receive(message)

    async def receive(self, message):
        """Receives message from current channel."""
        pass

    async def send_to_channel(self, channel, message):
        """Sends the given message to the given channel."""
        try:
            await self.channel_layer.send(channel, message)
        except AttributeError:
            raise InvalidChannelLayerError(
                "BACKEND is not configured or doesn't support groups")

    async def send_to_group(self, group, message):
        """Sends the given message to the given group."""
        try:
            await self.channel_layer.group_send(group, message)
        except AttributeError:
            raise InvalidChannelLayerError(
                "BACKEND is not configured or doesn't support groups")
