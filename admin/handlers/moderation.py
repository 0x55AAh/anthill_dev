from ._base import ServicePageHandler


class ModerationPageHandler(ServicePageHandler):
    service_name = 'moderation'


class IndexHandler(ModerationPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
