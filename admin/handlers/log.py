from ._base import ServicePageHandler


class LogPageHandler(ServicePageHandler):
    service_name = 'log'


class IndexHandler(LogPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
