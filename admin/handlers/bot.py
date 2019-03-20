from ._base import ServicePageHandler


class BotPageHandler(ServicePageHandler):
    service_name = 'bot'


class IndexHandler(BotPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
