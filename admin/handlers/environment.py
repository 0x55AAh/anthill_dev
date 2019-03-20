from ._base import ServicePageHandler


class EnvironmentPageHandler(ServicePageHandler):
    service_name = 'environment'


class IndexHandler(EnvironmentPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['environments_list'] = []  # TODO:
        return context
