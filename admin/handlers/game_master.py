from ._base import ServicePageHandler


class GamePageHandler(ServicePageHandler):
    service_name = 'game_master'


class IndexHandler(GamePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['deployments_list'] = []  # TODO:
        return context
