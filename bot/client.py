from anthill.platform.core.messenger.message import MessengerClient
from bot.actions.exceptions import ActionError
import socketio
import logging

logger = logging.getLogger('anthill.application')


class _SocketIOClientNamespace(socketio.AsyncClientNamespace):
    def __init__(self, bot, namespace=None):
        super().__init__(namespace)
        self.bot = bot

    def on_connect(self):
        logger.debug('Bot %s connected to messenger.' % self.bot)

    def on_disconnect(self):
        logger.debug('Bot %s disconnected from messenger.' % self.bot)

    async def on_message(self, data):
        for action in self.bot.actions:
            try:
                await action.value_object.on_message(data, emit=self.emit)
            except ActionError:
                pass


class BotClient(MessengerClient):
    def __init__(self, bot, url, namespace='/messenger'):
        self.bot = bot
        super().__init__(url, namespace)

    def register_namespace(self):
        self._client.register_namespace(_SocketIOClientNamespace(self.bot, self.namespace))
