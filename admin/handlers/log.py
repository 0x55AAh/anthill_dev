from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin


class LogPageHandler(ServicePageHandler):
    service_name = 'log'


class LogFormHandler(FormMixin, ProcessFormMixin, LogPageHandler):
    pass


class IndexHandler(LogPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
