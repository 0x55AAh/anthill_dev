from ._base import ServicePageHandler


class EventPageHandler(ServicePageHandler):
    service_name = 'event'


class IndexHandler(EventPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
