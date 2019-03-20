from ._base import ServicePageHandler


class ConfigPageHandler(ServicePageHandler):
    service_name = 'config'


class IndexHandler(ConfigPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['configs_list'] = []  # TODO:
        return context
