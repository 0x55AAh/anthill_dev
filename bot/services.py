from anthill.framework.utils.asynchronous import as_future
from anthill.platform.services import PlainService
from bot.client import BotClient
from bot.models import Bot


class Service(PlainService):
    """Anthill default service."""

    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        super().__init__(handlers, default_host, transforms, **kwargs)
        self.bot_clients = []

    @as_future
    def get_bot_clients(self):
        url = self.get_service_location(self.message_name, 'internal')
        bots = Bot.query.filter_by(enabled=True)
        return map(lambda bot: BotClient(bot, url), bots)

    async def on_start(self) -> None:
        await super().on_start()
        self.bot_clients = await self.get_bot_clients()
        for bot_client in self.bot_clients:
            await bot_client.connect()

    async def on_stop(self) -> None:
        for bot_client in self.bot_clients:
            await bot_client.close()
        await super().on_stop()
