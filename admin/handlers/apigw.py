from ._base import ServicePageHandler


class ApiGWPageHandler(ServicePageHandler):
    service_name = 'apigw'


class IndexHandler(ApiGWPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
