from ._base import ServicePageHandler


class SocialPageHandler(ServicePageHandler):
    service_name = 'social'


class IndexHandler(SocialPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
