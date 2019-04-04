from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin


class MediaPageHandler(ServicePageHandler):
    service_name = 'media'


class MediaFormHandler(FormMixin, ProcessFormMixin, MediaPageHandler):
    pass


class IndexHandler(MediaPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
