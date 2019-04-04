from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin


class SocialPageHandler(ServicePageHandler):
    service_name = 'social'


class SocialFormHandler(FormMixin, ProcessFormMixin, SocialPageHandler):
    pass


class IndexHandler(SocialPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
