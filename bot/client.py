from anthill.platform.core.messenger.message import MessengerClient
from bot.actions.exceptions import ActionError
import socketio
import logging
import functools

logger = logging.getLogger('anthill.application')


class _SocketIOClientNamespace(socketio.AsyncClientNamespace):
    def __init__(self, bot, namespace=None):
        super().__init__(namespace)
        self.bot = bot

    async def on_connect(self):
        # TODO: join self.bot.connect_groups
        logger.debug('Bot %s connected to messenger.' % self.bot)

    async def on_disconnect(self):
        logger.debug('Bot %s disconnected from messenger.' % self.bot)

    async def on_message(self, data):
        for action in self.bot.actions:
            try:
                emit = functools.partial(self.emit, event='message')
                await action.value_object.on_message(data, emit=emit)
                # TODO: reply?
            except ActionError:
                logger.error('Action `%s` cannot process message %s.' % (action, data))


class BotClient(MessengerClient):
    def __init__(self, bot, url, namespace='/messenger'):
        self.bot = bot
        super().__init__(url, namespace)

    def register_namespace(self):
        self._client.register_namespace(_SocketIOClientNamespace(self.bot, self.namespace))
