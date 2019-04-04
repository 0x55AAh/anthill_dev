from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin


class ExecPageHandler(ServicePageHandler):
    service_name = 'exec'


class ExecFormHandler(FormMixin, ProcessFormMixin, ExecPageHandler):
    pass


class IndexHandler(ExecPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['commits_list'] = []  # TODO:
        return context
