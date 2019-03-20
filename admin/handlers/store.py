from ._base import ServicePageHandler


class StorePageHandler(ServicePageHandler):
    service_name = 'store'


class IndexHandler(StorePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
