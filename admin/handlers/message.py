from ._base import ServicePageHandler


class MessagePageHandler(ServicePageHandler):
    service_name = 'message'


class IndexHandler(MessagePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['groups_list'] = []  # TODO:
        return context
