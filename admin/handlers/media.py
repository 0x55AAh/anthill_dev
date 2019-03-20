from ._base import ServicePageHandler


class MediaPageHandler(ServicePageHandler):
    service_name = 'media'


class IndexHandler(MediaPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
