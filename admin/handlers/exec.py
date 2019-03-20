from ._base import ServicePageHandler


class ExecPageHandler(ServicePageHandler):
    service_name = 'exec'


class IndexHandler(ExecPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
