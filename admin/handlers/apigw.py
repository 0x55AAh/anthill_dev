from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin


class ApiGWPageHandler(ServicePageHandler):
    service_name = 'apigw'


class ApiGWFormHandler(FormMixin, ProcessFormMixin, ApiGWPageHandler):
    pass


class IndexHandler(ApiGWPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
